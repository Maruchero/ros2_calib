# TODO

[x] - quando si carica la bag controllare se fisheye usare cv2.fisheye_undistort
- applicare rdf_to_flu quando si esporta la calibrazione
  - testare mettendo una nuova trasformazione in calib_manager.yaml
- investigare sull'algoritmo di calibrazione automatica
  - controllare che usi pnp (perspective end point)

[x] - Make calib_manager.yaml file required (it's optional now)
[ ] - Fix frame selection view: for some reason there is only one frame shown

altre piccole modifiche che sarebbero carine
[x] - mettere un alpha di trasparenza alla cloud per vedere attraverso i punti
[x] - non dover cliccre su apply view changes ogni volta ma che venga aggiornata in automatico quando cambia qualcosa in quelle impostazioni
[x] - possibilità di passare a riga di comando bag, file calibrazione, topic camera e topic lidar su cui fare le calibrazioni per skippare tutta la scelta iniziale

Prioritario:
[x] - verificare il funzionamento dell'algoritmo che trova la matrice di trasformazione tra un nodo e l'altro
[x] - verificare dove viene usato il suddetto algoritmo per capire se è tutto invertito
  [x] - usata anche nella results view, 3 volte: verificare se va invertita anche lì
  [x] - BUG l'esportazione della calibrazione non funziona
  [ ] - sistemato, bastava convertire in radianti. Ma c'è ancora qualche problema: nella transform view i valori rpy sembrano errati, ma poi quando si passa alla calibration view sono corretti
  [ ] - verificare che l'esportazione della calibrazione funzioni anche con source_frame e target_frame diversi da quelli originali
[x] - modificare l'applicazione delle rotazioni in modo che applichi una matrice di rotazione sopra a quella degli estrinseci
[x] - sistemare rectify image perché cancella i punti del lidar
