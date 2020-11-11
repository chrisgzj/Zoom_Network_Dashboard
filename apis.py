import http.client
import json, csv, time
from urllib.parse import quote
from Datos.credentials import get_token

sec_token = get_token()
conn = http.client.HTTPSConnection("api.zoom.us")
headers = {
    'authorization': "Bearer " + sec_token,
    'content-type': "application/json"
    }

def download_meeting_info():
    link_basic = "/v2/metrics/meetings?type=past&from=2020-11-01&to=2020-11-11&page_size=300"
    reuniones = []
    next_page = ''
    contador = 0
    while next_page != '' or reuniones == []:
        if next_page == '':
            conn.request("GET", link_basic, headers=headers)
        else:
            conn.request("GET", link_basic + "&next_page_token=" + next_page, headers=headers)
        res = conn.getresponse()
        datos = json.load(res)
        print(datos)
        [reuniones.append(reu) for reu in datos['meetings']]
        next_page = datos['next_page_token']
        contador += 1
        print(contador)
        time.sleep(2)
    with open('Datos/reuniones_nov.json', 'w') as outfile:
        json.dump(reuniones, outfile)

def filter_meetings():
    with open('reuniones_oct.json', 'r') as infile:
        reuniones = json.load(infile)
    with open('ids_clases.json', 'r') as infile:
        ids_clases = json.load(infile)
    reuniones_clase = [reu for reu in reuniones if reu['id'] in ids_clases]
    print(len(reuniones_clase))
    print(reuniones_clase[0])
    with open('reunionesclase_oct.json', 'w') as outfile:
        json.dump(reuniones_clase, outfile)

def download_participant_info():
    with open('reunionesclase_oct.json', 'r') as infile:
        reuniones = json.load(infile)

    uuids = [reu['uuid'] for reu in reuniones]

    participantes = {}

    uuids = uuids[1227:] #Dice que el 1226 no existe!
    print(len(uuids))

    for uuid in uuids:
        encoded_uuid = quote(uuid, safe='')
        double_encoded = quote(encoded_uuid, safe='')
        link = "/v2/metrics/meetings/" + double_encoded +"/participants?type=past&page_size=300"
        conn.request("GET", link, headers=headers)
        res = conn.getresponse()
        datos = json.load(res)
        print(datos)
        next_page = datos['next_page_token']
        list_participantes = datos['participants']
        while (next_page != ''):
            conn.request("GET", link + "&next_page_token=" + next_page, headers=headers)
            res = conn.getresponse()
            datos = json.load(res)
            next_page = datos['next_page_token']
            [list_participantes.append(dato) for dato in datos['participants']]
        print(datos['total_records'], " vs. ", len(list_participantes))
        participantes[uuid] = list_participantes
        with open('participantes_oct.json', 'w') as outfile:
            json.dump(participantes, outfile)
        time.sleep(1)

def extract_failures():
    with open('Datos/participantes_oct.json', 'r') as infile:
        participantes = json.load(infile)
    individuales = []
    [[individuales.append(part) for part in ls] for ls in participantes.values()]
    print(len(individuales))
    razones = {}
    razones['sin_razon'] = 0
    razones['razon_vacia'] = 0
    fallas = []
    for indiv in participantes:
        indi = participantes[indiv]
        for ind in indi:
            if 'leave_reason' in ind:
                razon = ind['leave_reason']
                if razon != '':
                    razon = razon[razon.index("<br>") + 12:]
                    if razon in razones:
                        razones[razon] += 1
                    else:
                        razones[razon] = 1
                else:
                    razones['razon_vacia'] += 1
                if razon == 'Network connection error. ':
                    ind['meeting_uuid'] = indiv
                    # participantes[indiv]['meeting_id'] = indiv
                    fallas.append(ind)
            else:
                razones['sin_razon'] += 1
    print(razones)
    # with open('participantes_oct.json', 'w') as outfile:
    #     json.dump(particip1, outfile)
    print(len(fallas))
    print(fallas[0])
    with open('Datos/fallas_oct.json', 'w') as outfile:
        json.dump(fallas, outfile)

def dicc_uuid():
    with open('Datos/reunionesclase_oct.json', 'r') as infile:
        reuniones = json.load(infile)
    uuids = {}
    for reu in reuniones:
        uuids[reu['uuid']] = reu['id']
    print (uuids)
    print (len(uuids))
    with open('Datos/uuids_oct.json', 'w') as outfile:
        json.dump(uuids, outfile)

def analyze_failures():
    with open('Datos/fallas_oct.json', 'r') as infile:
        fallas = json.load(infile)
    with open('Datos/uuids_oct.json', 'r') as infile:
        uuids = json.load(infile)
    fallas_grupales = {}
    for falla in fallas:
        id = (falla['meeting_uuid'], falla['leave_time'])
        if id in fallas_grupales:
            fallas_grupales[id] += 1
        else:
            fallas_grupales[id] = 1
    # print(fallas_grupales)
    print(len(fallas_grupales.values()))
    [print(ejem, uuids[ejem[0]], fallas_grupales[ejem]) for ejem in fallas_grupales if fallas_grupales[ejem] >= 10]

def analyze_others():
    with open('Datos/fallas_oct.json', 'r') as infile:
        fallas = json.load(infile)
    with open('Datos/uuids_oct.json', 'r') as infile:
        uuids = json.load(infile)
    dato_interes = {}
    dato_interes['sin_dato'] = 0
    for falla in fallas:
        dato = 'pc_name'
        try:
            if falla[dato] in dato_interes:
                dato_interes[falla[dato]] += 1
            else:
                dato_interes[falla[dato]] = 1
        except:
            dato_interes['sin_dato'] += 1
    print(dato_interes)
    print(sorted(dato_interes.values()))
    [print(ejem, dato_interes[ejem]) for ejem in dato_interes if dato_interes[ejem] >= 100]

def export_individual_failures():
    with open('Datos/fallas_oct.json', 'r') as infile:
        fallas = json.load(infile)
    with open('Datos/uuids_oct.json', 'r') as infile:
        uuids = json.load(infile)
    with open('Datos/clases.json', 'r') as infile:
        clases = json.load(infile)
    with open('Datos/secciones.json', 'r') as infile:
        secciones = json.load(infile)
    print(len(fallas))
    encabezado = ['fecha','uuid','id','clase','seccion','mail','IP','device','network_type','data_center','user_name']
    with open('Datos/fallas_ind_oct.csv', mode='w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(encabezado)
        for falla in fallas:
            uuid = falla['meeting_uuid']
            id = str(uuids[uuid])
            if 'email' in falla:
                email = falla['email']
            else:
                email = ""
            fila = [falla['leave_time'][:10], uuid, id, clases[id], secciones[id], email, falla['ip_address'], falla['device'], falla['network_type'], falla['data_center'], falla['user_name']]
            writer.writerow(fila)
            # print(fila),

def export_group_failures():
    with open('Datos/fallas_oct.json', 'r') as infile:
        fallas = json.load(infile)
    with open('Datos/uuids_oct.json', 'r') as infile:
        uuids = json.load(infile)
    with open('Datos/clases.json', 'r') as infile:
        clases = json.load(infile)
    with open('Datos/secciones.json', 'r') as infile:
        secciones = json.load(infile)
    fallas_grupales = {}
    for falla in fallas:
        id = (falla['meeting_uuid'], falla['leave_time'])
        if id in fallas_grupales:
            fallas_grupales[id] += 1
        else:
            fallas_grupales[id] = 1
    print(len(fallas_grupales))
    encabezado = ['fecha', 'hora', 'uuid', 'id', 'clase', 'seccion', 'num_desconect']
    conteo = 0
    suma = 0
    with open('Datos/fallas_grup_oct.csv', mode='w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(encabezado)
        for falla in fallas_grupales:
            if fallas_grupales[falla] >= 3:
                conteo += 1
                suma += fallas_grupales[falla]
                id = str(uuids[falla[0]])
                fila = [falla[1][:10], falla[1][11:19], falla[0], id, clases[id], secciones[id], fallas_grupales[falla]]
                writer.writerow(fila)
    print(conteo)
    print(suma)

download_meeting_info()