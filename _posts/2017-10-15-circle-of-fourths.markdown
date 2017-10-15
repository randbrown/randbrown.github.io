---
layout: post
title:  "Circle of Fourths with Inversions"
date:   2017-10-15 17:24:53 -0400
categories: jekyll update
---

<style type="text/css">
.image-flow {
  display: block;
  margin-left: auto;
  margin-right: auto;
  /* max-width: 50%; */
  float: left;
}
</style>

I've been exploring Python and NumPy for synthesizing music.  One program I wrote generates circles of fourths, with harmonic seventh chords, and inverts the chords such that all tones fall within a single octave.  This gives the feeling of a never ending descent of fifths or ascent of fourths (whichever way you choose to look at it).

First, take a listen:

<iframe width="100%" height="265" src="https://clyp.it/wz42dsgb/widget" frameborder="0"></iframe>

## The Theory

The [Circle of Fifths](https://en.wikipedia.org/wiki/Circle_of_fifths) can also be thought of as a circle of fourths.  So we start at A (specifically, A3 which is 220 Hz), and work our way around the circle of fifths in a counter-clockwise fashion.
![alt text](https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Circle_of_fifths_deluxe_4.svg/400px-Circle_of_fifths_deluxe_4.svg.png "Circle of Fifths"){: .image-flow }

We start at A, working counter-clockwise, to D, G, and so on, until finally ending on E.  Since we'll be repeating the whole sequence, the E resolves back to the A and the process continues on.

## The Code

The interesting parts of the code are below.  

I used my [PyWaveTools](https://github.com/randbrown/PyWaveTools) library to do some of the synthesis. I set the base root note to 220 Hz which is A3.  Then we build an array of NOTES to hold all the root notes, stacking in fourths, by multiplying each by 4/3 (which represents a perfect fourth interval).


```python
import wavelib
SAMPLE_RATE = 44100.0
NOTE = 220.0 # A3
NOTES = [NOTE]
note = NOTE
for i in range(1, 12):
    note = note * 4.0/3.0 # perfect fourth interval
    NOTES.append(note)
```

I decided to play each note for one second, so we set up the total duration, and use PyWaveTools to build an array of times for the whole buffer.

```python
NOTE_DURATION = 1   # play each n seconds
DURATION = len(NOTES) * NOTE_DURATION
times = wavelib.createtimes(DURATION, SAMPLE_RATE)
```

I wanted to keep all of the tones within the same interval, so I set min/max notes to constrain my frequencies to a single octave (in this case, from A3 to A4).

```python
# keep it within one octave, so we'll invert as needed
notemin = NOTE
notemax = NOTE * 2
```

The intervals array holds all the intervals of each given root note we will generate. In this case, I want a Root note (1), major 3rd (5/4 interval), a perfect fifth (3/2 interval), and a harmonic seventh (7/4 interval).  I am using [Just Intonation](https://en.wikipedia.org/wiki/Just_intonation) intervals, rather here to minimize the "beats" which would be intolerable if using Equal Temperament.  I chose the harmonic seventh (as opposed to a normal minor seventh) to sweeten it, again reducing the beats within the chords.

```python
# use harmonic 7th (7/4 interval) for smoother beatless chord
intervals = [1.0, 5.0/4.0, 3.0/2.0, 7.0/4.0]
vals = wavelib.zero(times)
for i in range(len(intervals)):
    interval = intervals[i]
    freq = wavelib.zero(times)
    for n in range(len(NOTES)):
        note = NOTES[n]
        f = NOTES[n] * interval
        while f >= notemax:
            f = f / 2.0
        while f < notemin:
            f = f * 2.0
        startidx = int(n * NOTE_DURATION * SAMPLE_RATE)
        endidx = int(((n+1) * NOTE_DURATION) * SAMPLE_RATE)
        freq[startidx:endidx] = f
    vals += wavelib.sinewave(times, freq)
```

And finally, we normalize the wave values to get it to a consistent volume, use the play_n function to play the sequence a total of 5 times.  This gives us a full 60 seconds of cycling fourth chords.  

```python

vals = wavelib.normalize(vals)
vals = wavelib.play_n(vals, 5)
wavelib.write_wave_file('output/circle_fourths_chords.wav', vals)
```
