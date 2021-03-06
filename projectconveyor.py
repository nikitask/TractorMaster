#Written by Nikitas Kanellakopoulos, 11/11/2014
#creates an optical conveyer array, and projects it onto the SLM using holo_to_slm



import holo_to_slm,superpose,doe_add,bessel,displace
import qimage2ndarray as q2

def projectconveyor(phase = 0):
  amp1, phi1 = bessel.construct(30)
  amp2, phi2 = bessel.construct(20)
  print(amp1.shape, amp2.shape, phi1.shape, phi2.shape)
  phi, ampout = superpose.construct(phi1 + phase, phi2, amp1 = amp1, amp2 = amp2)
  phi3 = displace.construct(140,10)
  phiout = doe_add.construct(phi,phi3, amp1 = ampout)#removed amp2
  return phiout
