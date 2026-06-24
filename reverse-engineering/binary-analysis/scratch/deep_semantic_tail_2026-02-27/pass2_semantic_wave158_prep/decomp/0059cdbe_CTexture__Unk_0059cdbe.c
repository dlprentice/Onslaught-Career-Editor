/* address: 0x0059cdbe */
/* name: CTexture__Unk_0059cdbe */
/* signature: void __stdcall CTexture__Unk_0059cdbe(void * param_1, void * param_2) */


void CTexture__Unk_0059cdbe(void *param_1,void *param_2)

{
  byte bVar1;

  bVar1 = *(byte *)param_2;
  if (((((((bVar1 < 0x29) || (0x7a < bVar1)) || ((0x5a < bVar1 && (bVar1 < 0x61)))) ||
        ((bVar1 = *(byte *)((int)param_2 + 1), bVar1 < 0x29 || (0x7a < bVar1)))) ||
       ((0x5a < bVar1 && (bVar1 < 0x61)))) ||
      ((((bVar1 = *(byte *)((int)param_2 + 2), bVar1 < 0x29 || (0x7a < bVar1)) ||
        ((0x5a < bVar1 && (bVar1 < 0x61)))) ||
       ((bVar1 = *(byte *)((int)param_2 + 3), bVar1 < 0x29 || (0x7a < bVar1)))))) ||
     ((0x5a < bVar1 && (bVar1 < 0x61)))) {
    CDXTexture__LogChunkTagDiagnostic(param_1,0x5f3a34);
  }
  return;
}
