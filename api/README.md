# APIs

## Project

Build a quick-and-dirty data analysis using both public API data and raw web data. The base file uses Giantbomb.com video game prices and FRED STL USD inflation prices to contextualize them. 

**Note: The base project file's implementation of inflation calculation isn't really accurate (per the instructions) but I'm fixing that.**

## Running the Script

In its current form as uploaded, the script actually doesn't work. You will need to create a file called `giantbomb_api.py` that contains the following code:

```python
api_key = "MY_API_KEY"
```

where `MY_API_KEY` is the string received from Giantbomb [here](http://www.giantbomb.com/api/). 