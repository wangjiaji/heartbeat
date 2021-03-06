from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from models import Beat, Flag
from places.models import Place
from forms import BeatForm
from places.forms import PlaceForm
from heartbeat.http import HttpResponseForbidden, HttpResponseCreated, HttpResponseAccepted, HttpResponseOK

@login_required
@require_POST
def upload_beat(request):
    placeid = request.POST.get('places_id', 0)
    place_list = Place.objects.filter(pk=placeid)
    place = None
    if place_list:
        place = place_list[0]

    # Create the place if it's not there yet
    if not (placeid and place):
        place_form = PlaceForm(request.POST)
        if place_form.is_valid():
            place = place_form.save()
        else:
            return HttpResponseForbidden(place_form.errors)

    # Create the beat
    request.POST.update({'creator': request.user.id, 'place': placeid})
    beat_form = BeatForm(request.POST, request.FILES)
    if beat_form.is_valid():
        beat = beat_form.save(commit=False)
        beat.geohash = place.geohash
        beat.save()
        beat.update_tags()
        place.add_beat(beat.id)
        request.user.add_place(placeid)
        request.user.distribute_feed(beat.id)
        resp = HttpResponseCreated()
        resp['Location'] = '/api/v1/beats/%d' % beat.id
        return resp
    else:
        return HttpResponseForbidden(beat_form.errors)

@require_POST
@login_required
def add_heart(request, beatid):
    beat = get_object_or_404(Beat, pk=beatid)
    if request.POST.get('action', 'add') != 'remove':
        beat.add_heart(request.user)
        request.user.add_heart(beat)
    else:
        beat.del_heart(request.user)
        request.user.del_heart(beat)
    return HttpResponseAccepted()

@require_GET
def get_hot_beats(request):
    data = [x[0] for x in Beat.objects.only('id').values_list('id')]
    return HttpResponseOK(data)
    #    return HttpResponseOK(Beat.get_global_list('hot'))

@require_POST
@login_required
def flag_beat(request, beatid):
    try:
        beat = Beat.objects.only('id').get(id=beatid)
    except Beat.DoesNotExist:
        return HttpResponseForbidden({'error': 'beat not exist'})

    flag = Flag(creator=request.user, beat=beat)
    flag.save()
    return HttpResponseOK()

@require_GET
def search_beat_by_keyword(request, keyword):
    start = request.GET.get('start', 0)
    end = request.GET.get('end', -1)
    results = Beat.get_global_list('tag:' + keyword, start, end)
    return HttpResponseOK(results)
