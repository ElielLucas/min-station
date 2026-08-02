# min-station-project

Provavelmente, será necessário clonar o repositório do TNTP dentro desse repositório para que a geração de instâncias funcione.
Link: https://github.com/bstabler/TransportationNetworks

## Gerar instância (TPTP → MIN-STATION)
```bash
python gen_min_station.py   --repositorio ./TransportationNetworks   --caso Philadelphia   --saida inputs/Philadelphia.txt   --n-nos 800   --m-st 6   --percentil-r 0.5   --reindexar
```

## Executar modelos
### Baseline (fluxo)
```bash
python modelo_min_station_fluxo.py   --inputs-dir ./inputs   --csv-out results_min_station_baseline.csv   --time-limit 1200   --plots-dir ./plots_base
```

### Estendido
```bash
python modelo_estendido.py   --inputs-dir ./inputs   --csv-out results_min_station_ext.csv   --time-limit 1200   --plots-dir ./plots_ext
```
