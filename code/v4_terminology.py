"""Shared final terminology refinements for the prose and its rebuild."""
REPLACEMENTS={
 'ENSO, the Indian Ocean Dipole and the Southern Annular Mode have':'El Niño–Southern Oscillation (ENSO), the Indian Ocean Dipole (IOD) and the Southern Annular Mode (SAM) have',
 'The six nonnegative parameters minimise the continuous ranked probability score':'The six nonnegative parameters minimise the closed-form continuous ranked probability score',
 'Lower values are better. CRPSS is one minus':'Lower values are better. The corresponding skill score, CRPSS, is one minus',
 'Neither geographical proximity nor estimated error covariance reliably identifies where aggregate climate information will add skill in these experiments.':'Estimated covariance therefore provides an unreliable guide to realised gains in this sample.',
}
def refine(s):
 for a,b in REPLACEMENTS.items():s=s.replace(a,b)
 return s
if __name__=='__main__':
 from common import ROOT
 p=ROOT/'revision/review_v4/manuscript.md';p.write_text(refine(p.read_text(encoding='utf-8')),encoding='utf-8')
