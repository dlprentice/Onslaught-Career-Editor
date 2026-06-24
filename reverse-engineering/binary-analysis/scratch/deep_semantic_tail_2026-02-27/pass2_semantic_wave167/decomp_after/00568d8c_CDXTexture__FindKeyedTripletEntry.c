/* address: 0x00568d8c */
/* name: CDXTexture__FindKeyedTripletEntry */
/* signature: int * __cdecl CDXTexture__FindKeyedTripletEntry(int param_1, void * param_2) */


int * __cdecl CDXTexture__FindKeyedTripletEntry(int param_1,void *param_2)

{
  int *piVar1;

  piVar1 = param_2;
  if (*(int *)param_2 != param_1) {
    do {
      piVar1 = piVar1 + 3;
      if ((int *)((int)param_2 + DAT_0065612c * 0xc) <= piVar1) break;
    } while (*piVar1 != param_1);
  }
  if (((int *)((int)param_2 + DAT_0065612c * 0xc) <= piVar1) || (*piVar1 != param_1)) {
    piVar1 = (int *)0x0;
  }
  return piVar1;
}
