# Program Gabaroni – navodila za zagon

## Namestitev
1. Kloniraj repozitorij:
   ```bash
   git clone <url_do_repozitorija>
   cd nalogiinsprejem
   ```
2. Namesti odvisnosti:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Zagon aplikacije
Zaženi glavni skript:
```bash
python ProgramGabaroni/main.py
```

## Podatkovna baza
- Privzeto aplikacija uporablja datoteko `ProgramGabaroni/sledenje.db`.
- Če imaš obstoječo bazo v korenu repozitorija (`sledenje.db`), jo bo program sam kopiral v `ProgramGabaroni/sledenje.db`.
- Če je tvoja baza na drugi lokaciji, uporabi gumb **"Izberi bazo (sledenje.db)"** in izberi pravilno datoteko. Pot se bo shranila v `ProgramGabaroni/db_path.txt`, da bo uporabljena pri naslednjih zagonih.
