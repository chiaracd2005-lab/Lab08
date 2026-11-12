from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato = []
        for dist in self._distributori: #itera sui distributori
            prezzi = dist.get_prezzi()
            prezzi_del_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]
            if prezzi_del_mese:
                media = sum(prezzi_del_mese) / len(prezzi_del_mese)
            else:
                media = 0.0
            risultato.append((dist.nome, media)) #ritorna la lista di tuple
        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        if giorno > 7: #caso terminale: abbiamo deciso i rifornimenti per tutti e 7 i giorni
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        #esplorazione delle scelte: ad ogni giorno possiamo scegliere uno dei distributori
        indice_giorno = giorno - 1  #indice 0 per giorno 1,ecc
        for dist in self._distributori:
            costo_carburante = prezzi_settimana[dist.id][indice_giorno] * 100 #100 litri

            costo_spostamento = 0
            if ultimo_distributore is not None and dist.id != ultimo_distributore:
                costo_spostamento = 5 #costo fisso: 5€ se cambiamo distributore rispetto al giorno precedente

            nuovo_costo = costo_corrente + costo_carburante + costo_spostamento

            if self.__costo_ottimo != -1 and nuovo_costo >= self.__costo_ottimo: #se il costo parziale supera già il miglior costo trovato ...
                continue

            sequenza_parziale.append(dist.id)  #passo ricorsivo

            self.__ricorsione(
                sequenza_parziale=sequenza_parziale,
                giorno=giorno + 1,
                ultimo_distributore=dist.id,
                costo_corrente=nuovo_costo,
                prezzi_settimana=prezzi_settimana
            )

            sequenza_parziale.pop() #rimuove la scelta corrente per permettere l'esplorazione corretta della ramificazione alternativa

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        diz_prezzi = {}
        for dist in self._distributori:
            prezzi = dist.get_prezzi()
            prezzi_settimana = [p for p in prezzi if p.data.month == mese and 1 <= p.data.day <= 7] #filtriamo i prezzi del mese e dei primi 7 giorni

            prezzi_settimana.sort(key=lambda p: p.data.day) #ordiniamo per data/giorno per garantire la sequenza cronologica

            diz_prezzi[dist.id] = [p.prezzo_litro for p in prezzi_settimana]

        return diz_prezzi