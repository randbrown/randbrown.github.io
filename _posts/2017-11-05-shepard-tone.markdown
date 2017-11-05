---
layout: post
title:  "The Shepard Tone"
date:   2017-11-05 16:56:00 -0500
categories: jekyll update
comments: true
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

I've been kind of obsessed with the [Shepard Tone](https://en.wikipedia.org/wiki/Shepard_tone) lately.  So
I decided to write a program to generate some various shepard tones.  I've been learning Python and
NumPy, so I added this to my [PyWaveTools](https://github.com/randbrown/PyWaveTools) repository.  In this post I'll focus on a rising glissando.

First, take a listen:

<iframe width="100%" height="265" src="https://clyp.it/hjmpmtxy/widget" frameborder="0"></iframe>

## The Theory

The Shepard Tone consists of a primary frequency, stacked with lower and higher octaves, such
that as the primary tone rises or falls away from a peak frequency, the highest and lowest voices 
are faded in or out to achieve a feeling of perpetual ascent or descent.

For example, consider a glissando of a primary tone rising from A3 to A4, with the peak frequency of A3. We'll
add a lower octave tone rising from A2 to A3 with its intensity (loudness) also rising during that
time.  It starts at the A2 with intensity 0 (inaudible), and rises to A3 at intensity 1.0 (full
volume).  Thus by the end of the gliss, the lower octave is ending on the same note/intensity where the primary tone started.
voice.  Similarly, we add a higher voice rising from A4 to A5.  It starts at A4 at full volume (intensity 1.0),
and as it rises, the loudness is reduced, ending at intensity 0 at A5.  So the
primary voice ends at the same note/intensity where the higher voice started.

## The Code

I used my [PyWaveTools](https://github.com/randbrown/PyWaveTools) library to do the synthesis using sine waves. 
We begin by creating a numpy array holding the times from 0 to 12 seconds.  We'll use a 12-second glissando,
so it averages one half step per second as it rises.

```python
    # times is array of values at each time slot of the whole wav file
    times = wavelib.createtimes(12.0)
```

For the tone generation, I use the sinewave function to build a primary tone and a tritone (diminished fifth).
I created a function for this, since my shepard tone function accepts a wave generation function argument.

```python
def tritone_sine(times, freq):
    vals1 = wavelib.sinewave(times, freq)
    vals2 = wavelib.sinewave(times, freq* wavelib.DIMINISHED_FIFTH)
    vals = vals1 + vals2
    return vals
```

Then I create a numpy array to hold the frequencies of the glissando.  We'll start at A3 and end at A4.
This function does linear<sup><a href="#fn1" id="ref1">1</a></sup> scaling from A3 to A4.

```python
    freq = wavelib.glissando_lin(times, wavelib.FREQ_A3, wavelib.FREQ_A4)
```

Then I call my shepardtone function, passing in the freqencies array, my wave generator function,
peak freqency of A3, one octave below and one octave above. 

```python
    vals = wavelib.shepardtone(times, freq, tritone_sine, wavelib.FREQ_A3, 1, 1)
```

Let's look at that shepardtone function.  First it generates the primary voice
and stores it in the vals array.  

Then it generates the lower voice(s) by
multiplying the frequencies by negative powers of 2.  For the lowest voice,
it also scales the intensity (loudness) of the voice based on how far away
the note is from the peak frequency.  In our example, the peak frequency
is A3, so as the tone rises from A3 to A4, the lower octave voice will
start at 0 intensity and rise to 1 (full intensity).  I achieve this by comparing the primary frequency to the peak frequency, and building a numpy
array of intensities called intsi.  The vals for this voice are multiplied by intsi to fade it in.

Similarly, I generate the higher voices by multiplying the frequencies by powers of 2.  For the highest, voice we do similar logic as before, but we want to fade it out as it rises, so we subtract the percentage of peak from 1 to achieve the fade out<sup><a href="#fn2" id="ref2">2</a></sup>.

```python
def shepardtone(times, freq, waveform_generator = sinewave, peak_freq=None, num_octaves_down=3, num_octaves_up=3):
    # primary tone is generated
    vals = waveform_generator(times, freq)

    # build the lower voice(s)
    for i in range(0, num_octaves_down):
        freqi = freq * 2.0**(-(i+1))
        valsi = waveform_generator(times, freqi)
        if i == (num_octaves_down-1):
            intsi = np.abs(freq - peak_freq)/peak_freq
            valsi = valsi * intsi
        vals += valsi

    # build the higher voice(s)
    for i in range(0, num_octaves_up):
        freqi = freq * 2.0**(i+1)
        valsi = waveform_generator(times, freqi)
        if i == (num_octaves_up-1):
            intsi = 1.0 - np.abs(peak_freq - freq)/peak_freq
            valsi = valsi * intsi
        vals += valsi

    return vals
```

And finally we normalize it, repeat it a total of 5 times for a total of 60 seconds, and write to file.

```python
    vals = wavelib.normalize(vals)
    vals = wavelib.play_n(vals, 5)
    wavelib.write_wave_file('output/shepard_tritone_up_5x.wav', vals)
```

## Falling glissando
Here is an example of falling instead of rising.  All the code is the same, except the frequency start/end are reversed.

<iframe width="100%" height="265" src="https://clyp.it/actuydtj/widget" frameborder="0"></iframe>


#### Notes

<a id="fn1" href="#ref1">1.</a>: Linear scaling works sufficiently for this example. However, with frequency,
our perception is not linear, so the glissando will sound like it rises faster as it gets higher.  To make a
more even sounding glissando, logarithmic scaling could be used.

<a id="fn2" href="#ref2">2.</a>: Similar to frequeny, we perceive loudness non-linearly.  This means our loudness fade in and fade out may sound somewhat abrupt.  To make the fades smoother, logarithmic scaling of the intensities could be used.

## Other Examples

My code and sounds in this post are very simplistic examples.  Others have made much more sophisticated sounds. 

Here is one of my favorites. Ten hours of falling shepard tone, with an excellent fractal display.  This is quite mesmorizing!
<iframe width="560" height="315" src="https://www.youtube.com/embed/u9VMfdG873E" frameborder="0" allowfullscreen></iframe>

Here is a great example of using the Shepard tone concept, but applied in a much more musical way. 
<iframe width="560" height="315" src="https://www.youtube.com/embed/A41CITk85jk" frameborder="0" allowfullscreen></iframe>

## Wrap Up
In this post I focused on using the Shepard tone with glissandos.  In my PyWaveTools repository there are also examples of Shepard tone with discrete chromatic scales, along with other various experiments with generating waveforms. 