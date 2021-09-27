# real-estate-scrape

Get the estimated value of a property from Redfin and Zillow

## Automated usage

![Plot of Redfin and Zillow estimated value as a function of time](https://github.com/mikepqr/real-estate-scrape-eg/data.png)

To make charts like this by getting the value of a property once a day and
storing the result, see
[mikepqr/real-estate-scrape-eg](https://github.com/mikepqr/real-estate-scrape-eg]).

## Advanced/manual usage

Export `REDFIN_URL` and `ZILLOW_URL`. To optionally use scraperapi, also export
`SCRAPERAPI_KEY`. Then to scrape and append to data.csv in the current working
directory:

    $ pip install real-estate-scrape
    $ real-estate-scrape

## Why

Redfin and Zillow both give you an estimate of the current market value of your
home. That estimate is given to the nearest dollar (!) and comes with a chart
that claims to be the history of that estimate. That historical chart is a lie.
The estimate for today bounces around a lot, but they retcon the history to
pretend it doesn't. The precision of today's estimate and the smoothness of the
chart make the estimate look ridiculously trustworthy. This scraper captures the
bouncing, which gives you a good idea how much to trust the current value
(probably good to 10-20% at most).

## Caveats

 - The Zillow scraper doesn't work if the house is on the market. The page
   layout changes and I can't figure out the xpath. PRs welcome.
