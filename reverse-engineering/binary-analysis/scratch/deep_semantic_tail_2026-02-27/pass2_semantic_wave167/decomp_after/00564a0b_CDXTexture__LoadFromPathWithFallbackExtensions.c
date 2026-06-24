/* address: 0x00564a0b */
/* name: CDXTexture__LoadFromPathWithFallbackExtensions */
/* signature: int __cdecl CDXTexture__LoadFromPathWithFallbackExtensions(int param_1, void * param_2, int param_3, int param_4) */


int __cdecl
CDXTexture__LoadFromPathWithFallbackExtensions(int param_1,void *param_2,int param_3,int param_4)

{
  char *pcVar1;
  char *pcVar2;
  size_t sVar3;
  char *pcVar4;
  int iVar5;
  void *pvVar6;
  undefined **ppuVar7;
  int local_c;

  pcVar1 = (char *)CRT__MbsRChr(param_2,0x5c);
  pcVar2 = (char *)CRT__MbsRChr(param_2,0x2f);
  pcVar4 = param_2;
  if (pcVar2 == (char *)0x0) {
    if ((pcVar1 != (char *)0x0) ||
       (pcVar1 = (char *)CRT__MbsChr(param_2,0x3a), pcVar1 != (char *)0x0)) goto LAB_00564a80;
    sVar3 = _strlen(param_2);
    pcVar4 = _malloc(sVar3 + 3);
    if (pcVar4 != (char *)0x0) {
      CRT__StrCpyAligned(pcVar4,&DAT_005e5de0);
      CRT__StrCatAligned(pcVar4,param_2);
      pcVar1 = pcVar4 + 2;
      goto LAB_00564a80;
    }
LAB_00564ad9:
    local_c = -1;
  }
  else {
    if ((pcVar1 == (char *)0x0) || (pcVar1 < pcVar2)) {
      pcVar1 = pcVar2;
    }
LAB_00564a80:
    local_c = -1;
    iVar5 = CRT__MbsRChr(pcVar1,0x2e);
    if (iVar5 == 0) {
      sVar3 = _strlen(pcVar4);
      pvVar6 = _malloc(sVar3 + 5);
      if (pvVar6 == (void *)0x0) goto LAB_00564ad9;
      CRT__StrCpyAligned(pvVar6,pcVar4);
      sVar3 = _strlen(pcVar4);
      ppuVar7 = &PTR_DAT_00653c1c;
      do {
        CRT__StrCpyAligned((void *)(sVar3 + (int)pvVar6),*ppuVar7);
        iVar5 = CDXTexture__Helper_0056a7e7((int)pvVar6,0);
        if (iVar5 != -1) {
          local_c = CDXTexture__LoadFromResolvedPathAndDecodedBuffer
                              (param_1,(int)pvVar6,param_3,param_4);
          break;
        }
        ppuVar7 = ppuVar7 + -1;
      } while (0x653c0f < (int)ppuVar7);
      CRT__FreeBase((int)pvVar6);
    }
    else {
      iVar5 = CDXTexture__Helper_0056a7e7((int)pcVar4,0);
      if (iVar5 != -1) {
        local_c = CDXTexture__LoadFromResolvedPathAndDecodedBuffer
                            (param_1,(int)pcVar4,param_3,param_4);
      }
    }
    if (pcVar4 != param_2) {
      CRT__FreeBase((int)pcVar4);
    }
  }
  return local_c;
}
