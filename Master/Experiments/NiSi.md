#NiSi
#cTLM
#Experiments

- Use cTLM process to quickly make samples
	- litho
	- metal stack deposition
	- lift-off
	- RTP
	- cTLM measurement
- complete wafer process required to deposit material stack
  -> different annealing conditions are possible using broken up wafer


- ### Annealing:
	- typical temps are 950 - 1000 °C 
	- the layer stack could potentially enable lower annealing temperatures
	  -> BUT: some papers state the importance of a silicide phase change at high temperatures

- determine material properties after annealing
  - XRD (get phase of Silicide)
  - Raman ?
  - SEM ?
  - FIBS 


=> first only use n-Type with the substrate doping 
-> Additional step with a full wafer implantation necessary 


### Metal stacks used:
- Stoichiometry: the desired silicide phase is targeted by the atomic ratio of the Ni and Si layers
  => $Ni_2Si$: 2 Ni atoms + 1 Si atom ratio
	- **Atomic Mass (A):**
	    - Ni ≈ 58.69 g/mol
	    - Si ≈ 28.09 g/mol
	- **Density (ρ):**
        - Ni (e-beam/sputtered) ≈ 8.91 g/cm³
		- Si (amorphous/poly) ≈ 2.33 g/cm³ (2,29-2,31 for a-Si)
- layer thickness ratio:
$$\begin{align}
t_{Ni} &= t_{Si} \cdot \frac{Ni}{Si} \cdot \frac{M_{Ni}}{M_{Si}} \cdot \frac{\rho_{Si}}{\rho_{Ni}} \\
       &= t_{Si} \cdot \frac{2}{1} \cdot \frac{58.69\,\text{g/mol}}{28.09\,\text{g/mol}} \cdot \frac{2.33\,\text{g/cm}^3}{8.91\,\text{g/cm}^3} \\
       &= t_{Si} \cdot 1.093
\end{align}
$$
		- use ~50 nm Ni => total ~100 nm

### Annealing conditions
- keep the 2 min peak annealing temp time
- keep N gas as innert gas (Ar theoretically better but not currently used)
- **Temperature:**
	- standard 980 °C for comparison
	- 800 °C as first step and see if this works -> maybe even lower temperatures are possible for ohmic contact formation


Overview over different layer compositions from paper:  

|                                                                                      |                            |            |                                         |                                                          |                                                                                                               |                                                                                                                                             |
| ------------------------------------------------------------------------------------ | -------------------------- | ---------- | --------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Material                                                                             | Annealing                  | Doping     | Contact Resitance                       | Notes                                                    | Publication                                                                                                   | DOI / URL                                                                                                                                   |
| Ni2Si  <br>6-HSiC/12 nm Si/13 nm Ni/12 nm Si/13 nm Ni                                | 960 °C 30 min              | 5.5×10^17  | 8×10^-4                                 |                                                          | Ni and Ni Silicides Ohmic Contacts on N-type 6H-SiC with Medium and Low Doping Level                          | [https://www.researchgate.net/publication/229020942](https://www.researchgate.net/publication/229020942)  <br>or: 10.1016/j.tsf.2012.02.008 |
| Ni2Si  <br>4-HSiC/12 nm Si/13 nm Ni/12 nm Si/13 nm Ni  <br>+ SiC/ 48 nm Si/ 52 nm Ni | 960 °C 30 min              | 4.2x10^18  | 8×10^-5                                 | Same author but this time 4and 6H                        |                                                                                                               |                                                                                                                                             |
| 6H-SiC<br><br>Ni/Si or Si/Ni in 2:1                                                  | 950 °C 10 min              | 1x10^19    | 1.2x^-5  <br>-> higher than only SiC/Ni | XPS  <br>-> less carbon in contact with Ni+Si deposition | Nickel based ohmic contacts on SIC                                                                            | [https://doi.org/10.1016/S0921-5107(96)01981-2](https://doi.org/10.1016/S0921-5107\(96\)01981-2)                                            |
| 4H-SiC Ni/Si/Ni/Si(33.1/30.3/33.1/30.3nm)/n-SiC                                      | 600 °C 15 min + 1050 3 min | 9.37x10^16 | 4.1x10^-4                               | Good surface                                             | Fabrication and characterization of nickel silicide ohmic contacts to n-type 4H silicon carbide               | 10.1088/1742-6596/100/4/042003                                                                                                              |
| Only Ni on 4H-SIC                                                                    |                            |            |                                         | P and n using Ni                                         | Thermal stability of the current transport mechanisms in Ni-based Ohmic contacts on n- and p-implanted 4H-SiC |                                                                                                                                             |
|                                                                                      |                            |            |                                         |                                                          |                                                                                                               |                                                                                                                                             |
=> layer thickness is limited by layer separation / adhesion when sputtering Ni

Swap Ni and Si layers to see if a reaction of the Ni and SiC surface is necessary (~600°C is sufficient) + NiSi is still made using the layers, therefore maybe lower temp required

=> most likely not, since NiSi alone is not the origin of ohmic behaviour

Some papers state that NiSi2 is also a desirable phase => should I make a sample making NiSi2 and one with Ni2Si

=> make a comparison sample using only Ni on SiC to get contact resistance and surface properties

