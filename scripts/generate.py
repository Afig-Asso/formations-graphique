import os, sys
import yaml
import json
import urllib.request, urllib.error
import argparse
import tqdm


meta = {
    'filename_yaml': 'data.yaml',
    'filename_json_out': 'json/data.json',
    'filename_md_out': 'README.md'
}
root_path = os.path.join(os.path.dirname(__file__))



def yaml_read_file(pathname):
    assert os.path.isfile(pathname)
    with open(pathname, 'r') as fid:
        content = yaml.safe_load(fid)
    return content



def checkurl(url):
    try:
        url_open = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if e.code==403: # server that doesn't allow non browser request
            return True
        print(f'Warning: URL seems down {url}')
        print('Error code: ', e.code)
        return False
    except urllib.error.URLError as e:
        print(f'Warning: URL seems wrong: {url}')
        print('Reason: ', e.reason)
        return False
    else:
        return True

def get_key_list_to_string(key, data, separator=', '):

    element = data[key]
    if isinstance(element,list):
        out = ', '.join(element)
    else:
        out = str(element)
    return out

def get_optional(key, data):
    if key in data:
        return get_key_list_to_string(key, data)
    else:
        return ''

def display_optional(s, indent=2, pre='* ', post='', bold=False, italic=False):

    additional_pre = ''
    additional_post = ''
    if bold==True:
        additional_pre = '**'
        additional_post = '**'
    if italic==True:
        additional_pre = '_'
        additional_post = '_'

    if s!='':
        space_fill = ' '*indent
        out = f'{space_fill}{pre}{additional_pre}{s}{additional_post}{post}\n'
        return out
    else:
        return ''

def prettyMD_master(name, data, is_check_url):
    out = ''
    

    
    url = data['url']
    if is_check_url:
        checkurl(url)



    title = get_optional('Title',data)
    city = get_optional('City',data)
    city_details = get_optional('City-detail',data)
    keywords = get_optional('Keywords', data )
    university = get_optional('University',data)

    international = False
    if 'International' in data:
        international = True

    city_txt = city
    if city_details!='':
        city_txt = city+', '+city_details

    out += f'* **[&#91;{name}&#93;]({url})** - **{title}** ({city_txt}) \n'
    if international:
        out += display_optional("_Master International entièrement en anglais_")
    out += display_optional(keywords, pre='* Mot clés: _', post='_')
    out += display_optional(university, pre='* Universités partenaires: _', post='_')


    out += '\n\n'

    return out

def prettyMD(data, is_check_url):

    out = '# Formations de Master en Informatique Graphique \n'
  
    out += '## Compléter/Modifier les informations \n'
    out += '  - Envoyez un email à contact[at]asso-afig.fr avec vos informations\n' 
    
    out += '\n\n'


    out += '## Listing \n\n' 
    

    keys = sorted(list(data['Listing'].keys()))
    for k in tqdm.tqdm(range(len(keys))):
        name = keys[k]
        element = data['Listing'][name]

        try:
            out += prettyMD_master(name, element, is_check_url)
        except KeyError as keyError:
            print('Key '+str(keyError)+' cannot be found in entry \n', element,'\n\n')
        except Exception as e:
            print("Undefined Problem with entry ",element)
            print(e)
            print()

    
    return out




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate Listing')
    parser.add_argument('-c','--checkURL', help='Check url validity', action='store_true')
    args = parser.parse_args()  

    is_check_url = args.checkURL

    filename_yaml = root_path+'/../'+meta['filename_yaml']
    filename_json_out = root_path+'/../'+meta['filename_json_out']
    filename_md_out = root_path+'/../'+meta['filename_md_out']


    data = yaml_read_file(filename_yaml)

    # export json
    with open(filename_json_out, 'w') as json_fid:
        json.dump(data, json_fid, indent=4)

    # export pretty md
    with open(filename_md_out, 'w') as md_fid:
        mdTXT = prettyMD(data, is_check_url)
        md_fid.write(mdTXT)