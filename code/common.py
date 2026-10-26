from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'_deps'))
REGIONS={
 'N':dict(name='Northern Australia',lon=(131.25,134.25),lat=(-15.75,-12.75),centres_lon=[132,133.5],centres_lat=[-15,-13.5]),
 'NE':dict(name='Northeastern Australia',lon=(146.25,149.25),lat=(-24.75,-21.75),centres_lon=[147,148.5],centres_lat=[-24,-22.5]),
 'SE':dict(name='Southeastern Australia',lon=(144.75,147.75),lat=(-36.75,-33.75),centres_lon=[145.5,147],centres_lat=[-36,-34.5]),
 'SW':dict(name='Southwestern Australia',lon=(116.25,119.25),lat=(-33.75,-30.75),centres_lon=[117,118.5],centres_lat=[-33,-31.5])}
