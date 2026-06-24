/* address: 0x0056004d */
/* name: CDXTexture__AsciiToLowerInPlace */
/* signature: char * __cdecl CDXTexture__AsciiToLowerInPlace(void * param_1) */


char * __cdecl CDXTexture__AsciiToLowerInPlace(void *param_1)

{
  char cVar1;
  size_t _Size;
  int iVar2;
  char *pcVar3;
  bool bVar4;
  void *local_c;

  local_c = (void *)0x0;
  if (DAT_009d0998 == 0) {
    cVar1 = *(char *)param_1;
    pcVar3 = param_1;
    while (cVar1 != '\0') {
      cVar1 = *pcVar3;
      if (('@' < cVar1) && (cVar1 < '[')) {
        *pcVar3 = cVar1 + ' ';
      }
      pcVar3 = pcVar3 + 1;
      cVar1 = *pcVar3;
    }
  }
  else {
    InterlockedIncrement(&DAT_009d35f0);
    bVar4 = DAT_009d35ec == 0;
    if (!bVar4) {
      InterlockedDecrement(&DAT_009d35f0);
      CDXTexture__Helper_00561179(0x13);
    }
    if (DAT_009d0998 == 0) {
      if (bVar4) {
        InterlockedDecrement(&DAT_009d35f0);
      }
      else {
        CTexture__Helper_005611da(0x13);
      }
      cVar1 = *(char *)param_1;
      pcVar3 = param_1;
      while (cVar1 != '\0') {
        cVar1 = *pcVar3;
        if (('@' < cVar1) && (cVar1 < '[')) {
          *pcVar3 = cVar1 + ' ';
        }
        pcVar3 = pcVar3 + 1;
        cVar1 = *pcVar3;
      }
    }
    else {
      _Size = CDXTexture__Helper_00565ee0();
      if (((_Size != 0) && (local_c = _malloc(_Size), local_c != (void *)0x0)) &&
         (iVar2 = CDXTexture__Helper_00565ee0(), iVar2 != 0)) {
        CDXTexture__Helper_00567de0(param_1,local_c);
      }
      if (bVar4) {
        InterlockedDecrement(&DAT_009d35f0);
      }
      else {
        CTexture__Helper_005611da(0x13);
      }
      CRT__FreeBase((int)local_c);
    }
  }
  return param_1;
}
