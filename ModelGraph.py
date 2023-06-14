import os
from pathlib import Path
import re
import logging
import pydot
import os
from datetime import datetime


def main():
    t = datetime.now().strftime('%d.%m.%Y %H-%M-%S')
    work_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    file_to_save = work_dir / f"output/images/"
    file_to_save.mkdir(parents=True, exist_ok=True)
    file_to_save = work_dir / f"output/images/ModelGraph_{t}.svg"

    file_log = work_dir / f"output/logs/"
    file_log.mkdir(parents=True, exist_ok=True)
    file_log = file_log / f'ModelGraph_{t}.log'

    some_file_dir = work_dir / f"output/some_files/"
    some_file_dir.mkdir(parents=True, exist_ok=True)

    data_dir = work_dir / 'data'
    
    file_log = logging.FileHandler(file_log, encoding='utf-8')
    console_out = logging.StreamHandler()

    logging.basicConfig(
        handlers=(file_log, console_out), 
        level=logging.INFO,
        format='[%(asctime)s | %(levelname)s]: %(message)s', 
        datefmt='%d.%m.%Y %H:%M:%S',
        )

    if data_dir.exists():
        logging.info(f'Start of graph creation')
        logging.info(f'Working directory {work_dir}, data directory {data_dir}')
    else:
        logging.error(f'{data_dir} path not found')
        raise FileNotFoundError()
    
    #TODO: добавить другие методы поиска зависимостей
    feeders_patern = r"^(?!#).*?=>\s*DB\(\s*'([^']+)"
    logging.info(f'Поиск зависимостей только на основе фидеров')

    dependency = []
    cube_list = []
    empty_rux = []
    for filename in os.listdir(data_dir):
        f = os.path.join(data_dir, filename)
        if filename.endswith('.RUX') and not filename.startswith('}'):
            cube_list.append(filename)
            
            textfile = open(f, 'r', encoding='UTF-8')
            filetext = textfile.read()
            textfile.close()

            all_db = []
            matches = re.findall(feeders_patern, filetext, flags=re.M)
            for match in matches:
                if match != filename[:-4] and (filename[:-4], match) not in all_db:
                    all_db.append((filename[:-4], match))
            if all_db != []:
                dependency.append(all_db)
            else:
                empty_rux.append(filename)

    with open(some_file_dir / f"empty_rux_{t}.txt", "w") as f:
        for s in empty_rux:
            f.write(f'{s}\n')

    #Create a graph object of directed type
    G = pydot.Dot(graph_type = "digraph",strict=True, concentrate=True, tooltip='')
    G.set_rankdir('TB')
    #G.set_overlap('prism')
    #G.set_overlap('orthoyx')
    #G.set_overlap_scaling('-0.4')
    G.set_ratio('0.4')
    #G.set_edge_defaults("'decorate'=True")
    #G.set_size('"5,8!"')
    #G.set_ratio("fill")

    for cube in dependency:
        for sourse, target in cube:
            edge = pydot.Edge(sourse, target, color="blue", decorate='true')
            G.add_edge(edge)
   
    try:
        #file_to_save = save_dir / f"ModelGraph_{dt_string}.svg"
        G.write_svg(file_to_save, encoding='utf-8')  
        logging.info(f'Image save in {file_to_save}')
    except Exception as e:
        print(e)
        logging.error(f'cannot save image')


if __name__ == '__main__':
    main()