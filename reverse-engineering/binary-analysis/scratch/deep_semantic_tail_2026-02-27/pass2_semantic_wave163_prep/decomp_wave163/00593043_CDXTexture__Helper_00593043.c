/* address: 0x00593043 */
/* name: CDXTexture__Helper_00593043 */
/* signature: void __stdcall CDXTexture__Helper_00593043(void * param_1, int param_2, int param_3) */


void CDXTexture__Helper_00593043(void *param_1,int param_2,int param_3)

{
  int *piVar1;
  char cVar2;
  byte bVar3;
  void *pvVar4;
  int iVar5;
  char *pcVar6;
  void *in_ECX;
  void *extraout_ECX;
  void *extraout_ECX_00;
  void *extraout_ECX_01;
  void *extraout_ECX_02;
  void *pvVar7;
  void *extraout_ECX_03;
  void *extraout_ECX_04;
  void *extraout_ECX_05;
  void *extraout_ECX_06;
  void *unaff_EBX;
  void *unaff_EDI;
  bool bVar8;
  uint uVar9;

  pvVar4 = param_1;
  if ((*(byte *)((int)param_1 + 0x5c) & 0x40) == 0) {
    CDXTexture__InitPngImageBuffersAndPassGeometry(param_1);
    in_ECX = extraout_ECX;
  }
  if ((*(char *)((int)pvVar4 + 0x113) != '\0') && ((*(byte *)((int)pvVar4 + 0x60) & 2) != 0)) {
    cVar2 = *(char *)((int)pvVar4 + 0x114);
    if (cVar2 == '\0') {
      if ((*(byte *)((int)pvVar4 + 0xd4) & 7) != 0) {
        bVar8 = param_3 == 0;
LAB_00593153:
        if (bVar8) goto LAB_005930aa;
        uVar9 = 0xff;
LAB_0059315e:
        CDXTexture__ExpandPackedPixelsToScanline((int)pvVar4,(void *)param_3,uVar9);
        in_ECX = extraout_ECX_00;
LAB_005930aa:
        CDXTexture__ProcessIdatChunkDataAndQueueDecode(in_ECX,(int)pvVar4,unaff_EDI);
        return;
      }
    }
    else if (cVar2 == '\x01') {
      if (((*(byte *)((int)pvVar4 + 0xd4) & 7) != 0) || (*(uint *)((int)pvVar4 + 0xb8) < 5)) {
        if (param_3 == 0) goto LAB_005930aa;
        uVar9 = 0xf;
        goto LAB_0059315e;
      }
    }
    else if (cVar2 == '\x02') {
      in_ECX = (void *)(*(uint *)((int)pvVar4 + 0xd4) & 0xffffff07);
      if ((char)in_ECX != '\x04') {
        if (param_3 == 0) goto LAB_005930aa;
        bVar8 = (*(uint *)((int)pvVar4 + 0xd4) & 4) == 0;
        goto LAB_00593153;
      }
    }
    else if (cVar2 == '\x03') {
      if (((*(byte *)((int)pvVar4 + 0xd4) & 3) != 0) || (*(uint *)((int)pvVar4 + 0xb8) < 3)) {
        if (param_3 == 0) goto LAB_005930aa;
        uVar9 = 0x33;
        goto LAB_0059315e;
      }
    }
    else if (cVar2 == '\x04') {
      in_ECX = (void *)(*(uint *)((int)pvVar4 + 0xd4) & 0xffffff03);
      if ((char)in_ECX != '\x02') {
        if (param_3 == 0) goto LAB_005930aa;
        bVar8 = (*(uint *)((int)pvVar4 + 0xd4) & 2) == 0;
        goto LAB_00593153;
      }
    }
    else if (cVar2 == '\x05') {
      if (((*(byte *)((int)pvVar4 + 0xd4) & 1) != 0) || (*(uint *)((int)pvVar4 + 0xb8) < 2)) {
        if (param_3 == 0) goto LAB_005930aa;
        uVar9 = 0x55;
        goto LAB_0059315e;
      }
    }
    else if ((cVar2 == '\x06') && ((*(byte *)((int)pvVar4 + 0xd4) & 1) == 0)) goto LAB_005930aa;
  }
  if ((*(byte *)((int)pvVar4 + 0x58) & 4) == 0) {
    CDXTexture__Helper_00592d45(pvVar4,0x5eea3c);
  }
  *(undefined4 *)((int)pvVar4 + 0x70) = *(undefined4 *)((int)pvVar4 + 0xdc);
  *(undefined4 *)((int)pvVar4 + 0x74) = *(undefined4 *)((int)pvVar4 + 0xcc);
  do {
    if (*(int *)((int)pvVar4 + 0x68) == 0) {
      if (*(int *)((int)pvVar4 + 0xfc) == 0) {
        do {
          CDXTexture__FinalizePngChunkAndVerifyCrc(pvVar4,0);
          CDXTexture__Helper_00595079(pvVar4,(int)&param_1,4);
          iVar5 = CDXTexture__ReadU32BigEndian(&param_1);
          *(int *)((int)pvVar4 + 0xfc) = iVar5;
          CDXTexture__InitDecodeSeedDefault((int)pvVar4);
          CTexture__Helper_0059cd4b(pvVar4,(int)pvVar4 + 0x10c,4);
          if (*(int *)((int)pvVar4 + 0x10c) != DAT_005ee8dc) {
            CDXTexture__Helper_00592d45(pvVar4,0x5eea24);
          }
        } while (*(int *)((int)pvVar4 + 0xfc) == 0);
      }
      *(uint *)((int)pvVar4 + 0x68) = *(uint *)((int)pvVar4 + 0xa0);
      *(int *)((int)pvVar4 + 100) = *(int *)((int)pvVar4 + 0x9c);
      if (*(uint *)((int)pvVar4 + 0xfc) < *(uint *)((int)pvVar4 + 0xa0)) {
        *(uint *)((int)pvVar4 + 0x68) = *(uint *)((int)pvVar4 + 0xfc);
      }
      CTexture__Helper_0059cd4b(pvVar4,*(int *)((int)pvVar4 + 0x9c),*(int *)((int)pvVar4 + 0x68));
      *(int *)((int)pvVar4 + 0xfc) = *(int *)((int)pvVar4 + 0xfc) - *(int *)((int)pvVar4 + 0x68);
    }
    iVar5 = CDXTexture__InflateStream_ProcessZlibState((int *)((int)pvVar4 + 100),1);
    if (iVar5 == 1) {
      if (((*(int *)((int)pvVar4 + 0x74) != 0) || (*(int *)((int)pvVar4 + 0x68) != 0)) ||
         (*(int *)((int)pvVar4 + 0xfc) != 0)) {
        CDXTexture__Helper_00592d45(pvVar4,0x5ee9f8);
      }
      *(uint *)((int)pvVar4 + 0x58) = *(uint *)((int)pvVar4 + 0x58) | 8;
      *(uint *)((int)pvVar4 + 0x5c) = *(uint *)((int)pvVar4 + 0x5c) | 0x20;
      break;
    }
    if (iVar5 != 0) {
      pcVar6 = *(char **)((int)pvVar4 + 0x7c);
      if (pcVar6 == (char *)0x0) {
        pcVar6 = "Decompression error";
      }
      CDXTexture__Helper_00592d45(pvVar4,(int)pcVar6);
    }
  } while (*(int *)((int)pvVar4 + 0x74) != 0);
  *(undefined1 *)((int)pvVar4 + 0xfa) = *(undefined1 *)((int)pvVar4 + 0x11a);
  *(undefined1 *)((int)pvVar4 + 0xf9) = *(undefined1 *)((int)pvVar4 + 0x117);
  *(byte *)((int)pvVar4 + 0xfb) = *(byte *)((int)pvVar4 + 0x119);
  *(undefined1 *)((int)pvVar4 + 0xf8) = *(undefined1 *)((int)pvVar4 + 0x116);
  piVar1 = (int *)((int)pvVar4 + 0xf0);
  *piVar1 = *(int *)((int)pvVar4 + 0xd0);
  *(uint *)((int)pvVar4 + 0xf4) =
       (uint)*(byte *)((int)pvVar4 + 0x119) * *(int *)((int)pvVar4 + 0xd0) + 7 >> 3;
  CDXTexture__ApplyPngScanlineFilter
            ((int)pvVar4,(int)piVar1,*(byte **)((int)pvVar4 + 0xdc) + 1,
             (void *)(*(int *)((int)pvVar4 + 0xd8) + 1),(uint)**(byte **)((int)pvVar4 + 0xdc));
  Memcpy(pvVar4,*(undefined4 *)((int)pvVar4 + 0xd8),*(undefined4 *)((int)pvVar4 + 0xdc),
         *(int *)((int)pvVar4 + 200) + 1);
  pvVar7 = extraout_ECX_01;
  if (*(int *)((int)pvVar4 + 0x60) != 0) {
    CDXTexture__Helper_00594d5c(pvVar4);
    pvVar7 = extraout_ECX_02;
  }
  if ((*(char *)((int)pvVar4 + 0x113) == '\0') || ((*(uint *)((int)pvVar4 + 0x60) & 2) == 0)) {
    if (param_2 != 0) {
      CDXTexture__ExpandPackedPixelsToScanline((int)pvVar4,(void *)param_2,0xff);
      pvVar7 = extraout_ECX_05;
    }
    if (param_3 == 0) goto LAB_0059339b;
    uVar9 = 0xff;
    pvVar7 = (void *)param_3;
  }
  else {
    bVar3 = *(byte *)((int)pvVar4 + 0x114);
    pvVar7 = (void *)CONCAT31((int3)((uint)pvVar7 >> 8),bVar3);
    if (bVar3 < 6) {
      CDXTexture__ExpandAdam7PassRowInPlace
                (piVar1,(void *)(*(int *)((int)pvVar4 + 0xdc) + 1),(uint)bVar3);
      pvVar7 = extraout_ECX_03;
    }
    if (param_3 != 0) {
      CDXTexture__ExpandPackedPixelsToScanline
                ((int)pvVar4,(void *)param_3,
                 *(uint *)(&DAT_005ee8b8 + (uint)*(byte *)((int)pvVar4 + 0x114) * 4));
      pvVar7 = extraout_ECX_04;
    }
    if (param_2 == 0) goto LAB_0059339b;
    uVar9 = *(uint *)(&DAT_005ee89c + (uint)*(byte *)((int)pvVar4 + 0x114) * 4);
    pvVar7 = (void *)param_2;
  }
  CDXTexture__ExpandPackedPixelsToScanline((int)pvVar4,pvVar7,uVar9);
  pvVar7 = extraout_ECX_06;
LAB_0059339b:
  CDXTexture__ProcessIdatChunkDataAndQueueDecode(pvVar7,(int)pvVar4,unaff_EBX);
  if (*(code **)((int)pvVar4 + 0x16c) != (code *)0x0) {
    (**(code **)((int)pvVar4 + 0x16c))
              (pvVar4,*(undefined4 *)((int)pvVar4 + 0xd4),*(undefined1 *)((int)pvVar4 + 0x114));
  }
  return;
}
