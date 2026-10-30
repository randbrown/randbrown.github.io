---
layout: home
list_title: Writing
---

<section class="home-hero">
  <figure class="home-hero-photo">
    <img src="/assets/pics/press/boot-scootin-mill-and-mine-2026-closeup.jpg" alt="Close-up of Randy Brown playing an Emmons pedal steel on stage">
    <figcaption>Boot Scootin' Boogie Nights · The Mill &amp; Mine, 2026 · photo: Eli Johnson</figcaption>
  </figure>
  <div class="home-hero-copy">
    <h1>Randy Brown</h1>
    <p class="home-tagline">pedal steel · guitar · live code · Knoxville, Tennessee</p>
    <p>I'm a musician and software developer. I play pedal steel in nightjar and the metal band Dysmorphic Demiurge, make ambient live-coded music as voidstar, and put out solo records as randbrown. This is where all of it lives, plus the occasional post.</p>
    <p class="home-booking">Booking: <a href="mailto:booking@randbrown.com">booking@randbrown.com</a> · <a href="https://instagram.com/randbrown">@randbrown</a></p>
  </div>
</section>

<h2 class="home-heading">Music</h2>

<div class="home-projects">
{%- for p in site.data.projects %}
  <div class="home-project">
    <img src="{{ p.thumb }}" alt="{{ p.name | escape }}" loading="lazy">
    <div>
      <h3>{{ p.name }}</h3>
      <p>{{ p.blurb }}</p>
      <p class="home-project-links">{% for l in p.links %}<a href="{{ l.href }}">{{ l.label }}</a>{% unless forloop.last %} · {% endunless %}{% endfor %}</p>
    </div>
  </div>
{%- endfor %}
</div>

<div class="home-tiles">
  <a href="/press/" class="home-tile"><strong>Press kit</strong> <span>bios, photos, billing, booking</span> </a>
  <a href="/music/" class="home-tile"><strong>Music</strong> <span>listen to the solo records</span> </a>
  <a href="/visioneer/" class="home-tile"><strong>Ramblin' Visioneer</strong> <span>got a sticker? start here</span> </a>
  <a href="/about/" class="home-tile"><strong>About</strong> <span>code, volunteering, side projects</span> </a>
</div>
