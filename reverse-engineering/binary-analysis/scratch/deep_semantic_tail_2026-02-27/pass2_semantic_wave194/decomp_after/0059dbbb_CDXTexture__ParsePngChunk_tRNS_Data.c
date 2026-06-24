/* address: 0x0059dbbb */
/* name: CDXTexture__ParsePngChunk_tRNS_Data */
/* signature: void __stdcall CDXTexture__ParsePngChunk_tRNS_Data(void * param_1, int param_2, uint param_3) */


void CDXTexture__ParsePngChunk_tRNS_Data(void *param_1,int param_2,uint param_3)

{
  char cVar1;
  void *pvVar2;
  int iVar3;
  char *pcVar4;
  undefined4 local_c;
  ushort local_8;

  if ((*(uint *)((int)param_1 + 0x58) & 1) == 0) {
    CDXTexture__ThrowDecodeError(param_1,0x5f3e5c);
  }
  else {
    if ((*(uint *)((int)param_1 + 0x58) & 4) != 0) {
      pcVar4 = "Invalid tRNS after IDAT";
LAB_0059dc2c:
      CDXTexture__ReportDecodeWarning((int)param_1,(int)pcVar4);
      CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,param_3);
      return;
    }
    if ((param_2 != 0) && ((*(byte *)(param_2 + 8) & 0x10) != 0)) {
      pcVar4 = "Duplicate tRNS chunk";
      goto LAB_0059dc2c;
    }
  }
  cVar1 = *(char *)((int)param_1 + 0x116);
  if (cVar1 == '\x03') {
    if ((*(byte *)((int)param_1 + 0x58) & 2) == 0) {
      CDXTexture__ReportDecodeWarning((int)param_1,0x5f3e40);
LAB_0059dbfd:
      if (param_3 != 0) {
        pvVar2 = CMeshCollisionVolume__Helper_0059cc7c(param_1,param_3);
        *(byte *)((int)param_1 + 0x5d) = *(byte *)((int)param_1 + 0x5d) | 0x20;
        *(void **)((int)param_1 + 0x15c) = pvVar2;
        CDXTexture__ReadChunkBytesAndUpdateCrc(param_1,(int)pvVar2,param_3);
        *(short *)((int)param_1 + 0x10a) = (short)param_3;
        goto LAB_0059dd17;
      }
      CDXTexture__ReportDecodeWarning((int)param_1,0x5f3e28);
    }
    else {
      if (param_3 <= *(ushort *)((int)param_1 + 0x108)) goto LAB_0059dbfd;
      CDXTexture__ReportDecodeWarning((int)param_1,0x5f3ddc);
    }
LAB_0059dd4f:
    CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,param_3);
  }
  else {
    if (cVar1 == '\x02') {
      if (param_3 != 6) {
LAB_0059dce5:
        pcVar4 = "Incorrect tRNS chunk length";
LAB_0059dd46:
        CDXTexture__ReportDecodeWarning((int)param_1,(int)pcVar4);
        goto LAB_0059dd4f;
      }
      CDXTexture__ReadChunkBytesAndUpdateCrc(param_1,(int)&local_c,6);
      *(short *)((int)param_1 + 0x162) = (short)((local_c & 0xff) * 0x100 + (local_c >> 8 & 0xff));
      *(ushort *)((int)param_1 + 0x164) = (ushort)local_c._2_1_ * 0x100 + (ushort)local_c._3_1_;
      *(ushort *)((int)param_1 + 0x166) = local_8 * 0x100 + (local_8 >> 8);
    }
    else {
      if (cVar1 != '\0') {
        pcVar4 = "tRNS chunk not allowed with alpha channel";
        goto LAB_0059dd46;
      }
      if (param_3 != 2) goto LAB_0059dce5;
      CDXTexture__ReadChunkBytesAndUpdateCrc(param_1,(int)&local_c,2);
      *(ushort *)((int)param_1 + 0x168) = (ushort)local_c * 0x100 + ((ushort)local_c >> 8);
    }
    *(undefined2 *)((int)param_1 + 0x10a) = 1;
LAB_0059dd17:
    iVar3 = CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,0);
    if (iVar3 == 0) {
      CDXTexture__SetDecodeOptionParams
                ((int)param_1,param_2,*(int *)((int)param_1 + 0x15c),
                 (uint)*(ushort *)((int)param_1 + 0x10a),(void *)((int)param_1 + 0x160));
    }
  }
  return;
}
