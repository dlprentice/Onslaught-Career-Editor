/* address: 0x0059d879 */
/* name: CDXTexture__ParsePngChunk_PLTE */
/* signature: void __stdcall CDXTexture__ParsePngChunk_PLTE(void * param_1, int param_2, uint param_3) */


void CDXTexture__ParsePngChunk_PLTE(void *param_1,int param_2,uint param_3)

{
  uint uVar1;
  void *pvVar2;
  void *pvVar3;
  int iVar4;
  undefined1 *puVar5;
  char *pcVar6;

  pvVar2 = param_1;
  uVar1 = *(uint *)((int)param_1 + 0x58);
  if ((uVar1 & 1) == 0) {
    pcVar6 = "Missing IHDR before PLTE";
LAB_0059d8a4:
    CDXTexture__Helper_00592d45(param_1,(int)pcVar6);
LAB_0059d8aa:
    *(uint *)((int)param_1 + 0x58) = *(uint *)((int)param_1 + 0x58) | 2;
    if (param_3 % 3 != 0) {
      pcVar6 = "Invalid palette chunk";
      if (*(char *)((int)param_1 + 0x116) != '\x03') goto LAB_0059d8ca;
      CDXTexture__Helper_00592d45(param_1,0x5f3bb8);
    }
    pvVar3 = (void *)((int)param_3 / 3);
    iVar4 = CDXTexture__AllocZeroedDecodeBuffer((int)param_1,(int)pvVar3,3);
    *(byte *)((int)param_1 + 0x5d) = *(byte *)((int)param_1 + 0x5d) | 0x10;
    if (0 < (int)pvVar3) {
      puVar5 = (undefined1 *)(iVar4 + 2);
      param_1 = pvVar3;
      do {
        CTexture__Helper_0059cd4b(pvVar2,(int)&param_3,3);
        puVar5[-2] = (undefined1)param_3;
        puVar5[-1] = param_3._1_1_;
        *puVar5 = param_3._2_1_;
        puVar5 = puVar5 + 3;
        param_1 = (void *)((int)param_1 + -1);
      } while (param_1 != (void *)0x0);
    }
    CDXTexture__FinalizePngChunkAndVerifyCrc(pvVar2,0);
    *(int *)((int)pvVar2 + 0x104) = iVar4;
    *(short *)((int)pvVar2 + 0x108) = (short)pvVar3;
    CTexture__Helper_00594fb6((int)pvVar2,param_2,iVar4,(int)pvVar3);
    if ((((*(char *)((int)pvVar2 + 0x116) == '\x03') && (param_2 != 0)) &&
        ((*(byte *)(param_2 + 8) & 0x10) != 0)) &&
       (*(ushort *)((int)pvVar2 + 0x108) < *(ushort *)((int)pvVar2 + 0x10a))) {
      CDXTexture__Helper_00592d63((int)pvVar2,0x5f3b90);
      *(ushort *)((int)pvVar2 + 0x10a) = *(ushort *)((int)pvVar2 + 0x108);
    }
  }
  else {
    if ((uVar1 & 4) == 0) {
      if ((uVar1 & 2) != 0) {
        pcVar6 = "Duplicate PLTE chunk";
        goto LAB_0059d8a4;
      }
      goto LAB_0059d8aa;
    }
    pcVar6 = "Invalid PLTE after IDAT";
LAB_0059d8ca:
    CDXTexture__Helper_00592d63((int)param_1,(int)pcVar6);
    CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,param_3);
  }
  return;
}
