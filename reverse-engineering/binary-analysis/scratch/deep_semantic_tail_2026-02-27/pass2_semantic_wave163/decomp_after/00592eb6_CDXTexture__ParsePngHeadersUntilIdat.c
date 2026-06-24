/* address: 0x00592eb6 */
/* name: CDXTexture__ParsePngHeadersUntilIdat */
/* signature: void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * param_1, int param_2) */


void CDXTexture__ParsePngHeadersUntilIdat(void *param_1,int param_2)

{
  int *piVar1;
  void *pvVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  char *pcVar6;

  pvVar2 = param_1;
  if (*(byte *)((int)param_1 + 0x11c) < 8) {
    uVar4 = (uint)*(byte *)((int)param_1 + 0x11c);
    uVar5 = -uVar4 + 8;
    CDXTexture__ReadFromSource(param_1,uVar4 + 0x20 + param_2,uVar5);
    *(undefined1 *)((int)pvVar2 + 0x11c) = 8;
    iVar3 = CDXTexture__ComparePngSignatureBytes(param_2 + 0x20,uVar4,uVar5);
    if (iVar3 != 0) {
      if (uVar4 < 4) {
        iVar3 = CDXTexture__ComparePngSignatureBytes(param_2 + 0x20,uVar4,-uVar4 + 4);
        if (iVar3 == 0) goto LAB_00592f1a;
        pcVar6 = "Not a PNG file";
      }
      else {
LAB_00592f1a:
        pcVar6 = "PNG file corrupted by ASCII conversion";
      }
      CDXTexture__ThrowDecodeError(pvVar2,(int)pcVar6);
    }
  }
  piVar1 = (int *)((int)pvVar2 + 0x10c);
  while( true ) {
    while( true ) {
      while( true ) {
        while( true ) {
          CDXTexture__ReadFromSource(pvVar2,(int)&param_1,4);
          uVar4 = CDXTexture__ReadU32BigEndian(&param_1);
          CDXTexture__InitDecodeSeedDefault((int)pvVar2);
          CTexture__Helper_0059cd4b(pvVar2,(int)piVar1,4);
          if (*piVar1 != DAT_005ee8d4) break;
          CDXTexture__ParsePngChunk_IHDR(pvVar2,param_2,uVar4);
        }
        if (*piVar1 != DAT_005ee8ec) break;
        CDXTexture__ParsePngChunk_PLTE(pvVar2,param_2,uVar4);
      }
      if (*piVar1 != DAT_005ee8e4) break;
      CDXTexture__ParsePngChunk_tRNS(pvVar2,param_2,uVar4);
    }
    if (*piVar1 == DAT_005ee8dc) break;
    if (*piVar1 == DAT_005ee8f4) {
      CDXTexture__ParsePngChunk_gAMA(pvVar2,param_2,uVar4);
    }
    else if (*piVar1 == DAT_005ee8fc) {
      CTexture__Helper_0059dad9(pvVar2,param_2,uVar4);
    }
    else if (*piVar1 == DAT_005ee904) {
      CTexture__Helper_0059dbbb(pvVar2,param_2,uVar4);
    }
    else {
      CTexture__Helper_0059dd5c(pvVar2,param_2,uVar4);
    }
  }
  if ((*(uint *)((int)pvVar2 + 0x58) & 1) == 0) {
    pcVar6 = "Missing IHDR before IDAT";
  }
  else {
    if ((*(char *)((int)pvVar2 + 0x116) != '\x03') || ((*(uint *)((int)pvVar2 + 0x58) & 2) != 0))
    goto LAB_00593013;
    pcVar6 = "Missing PLTE before IDAT";
  }
  CDXTexture__ThrowDecodeError(pvVar2,(int)pcVar6);
LAB_00593013:
  *(uint *)((int)pvVar2 + 0x58) = *(uint *)((int)pvVar2 + 0x58) | 4;
  *(uint *)((int)pvVar2 + 0xfc) = uVar4;
  return;
}
