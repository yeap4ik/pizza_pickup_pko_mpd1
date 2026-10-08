"Traveling salesman problem" picas adaptācijā.

Tiek dotas picerijas, kuras ir nepieciešāms apbraukāt ar divām mašīnām, lai izņemt visas pasūtītas picas no picerijam un piegadāt tos mājas. Ir zināms braukšanās laiks no vienas piecerijas uz katru citu, ka arī līdz mājām. Vērā tiek ņēmts arī picas gatavošanas laiks.

Ieejas dati: matrica ar braukšanas laikiem no mājas uz katru piceriju un starp picerijām, kā arī saraksts ar katras picerijas gatavošanas laiku.

Gājiens: nejauši izvēlētu picēriju pārvieto uz nejaušu pozīciju tās pašas vai otras mašīnas maršrutā.

Tiek izmantots SA algoritms.
Lai būtu iespēja parbaudīt optimizācijas rezultātu, uz mazām piceriju skaitām tiek izmantota pilna pārlase, lai atrastu garantēto labāko kombināciju un pēc tām salidzīnāt rezultātus ar SA iegūto kombināciju.

SA algoritms izmanto 10000 iterācijās, 10 mēģinājumus, sākuma temperatūra 20.0, beigu temperatūra 0.1.

Piemērs, kā izskatās matrica:

[0, 7, 10, 9]

[7, 0, 7, 13]

[10, 7, 0, 10]

[9, 13, 10, 0]

Matrica apzīmē nepieciešamo laiku, lai tiktu no vienas vietas uz citu. Matrica ir simetriska, jo braukšanas laiks turp un atpakaļ nemainās.
Piemēram, lai tiktu no mājām uz pirmo picēriju, ir nepieciešamas 7 minūtes. [0][1]
Lai tiktu no mājām uz otro picēriju, ir nepieciešamas 10 minūtes. [0][2]
Lai tiktu no pirmās picērijas uz otro, ir nepieciešamas 7 minūtes. [1][2]
Lai tiktu no pirmās picērijas uz trešo, ir nepieciešamas 13 minūtes. [1][3]
Lai tiktu no pirmās picērijas uz pirmo picēriju, ir nepieciešamas 0 minūtes. [1][1]
