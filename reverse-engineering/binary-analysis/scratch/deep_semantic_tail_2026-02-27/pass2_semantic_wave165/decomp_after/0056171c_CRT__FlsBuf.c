/* address: 0x0056171c */
/* name: CRT__FlsBuf */
/* signature: uint __cdecl CRT__FlsBuf(uint param_1, void * param_2) */


uint __cdecl CRT__FlsBuf(uint param_1,void *param_2)

{
  uint uVar1;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  undefined *puVar5;
  void *pvVar6;

  pvVar3 = param_2;
  uVar1 = *(uint *)((int)param_2 + 0xc);
  uVar2 = *(uint *)((int)param_2 + 0x10);
  if (((uVar1 & 0x82) == 0) || ((uVar1 & 0x40) != 0)) {
LAB_00561828:
    *(uint *)((int)param_2 + 0xc) = uVar1 | 0x20;
  }
  else {
    if ((uVar1 & 1) != 0) {
      *(undefined4 *)((int)param_2 + 4) = 0;
      if ((uVar1 & 0x10) == 0) goto LAB_00561828;
      *(undefined4 *)param_2 = *(undefined4 *)((int)param_2 + 8);
      *(uint *)((int)param_2 + 0xc) = uVar1 & 0xfffffffe;
    }
    uVar1 = *(uint *)((int)param_2 + 0xc);
    *(undefined4 *)((int)param_2 + 4) = 0;
    param_2 = (void *)0x0;
    *(uint *)((int)pvVar3 + 0xc) = uVar1 & 0xffffffef | 2;
    if (((uVar1 & 0x10c) == 0) &&
       (((pvVar3 != &DAT_006533e0 && (pvVar3 != &DAT_00653400)) ||
        (iVar4 = CRT__IsFdCommitMode(uVar2), iVar4 == 0)))) {
      CRT__InitFileBuffer(pvVar3);
    }
    if ((*(ushort *)((int)pvVar3 + 0xc) & 0x108) == 0) {
      pvVar6 = (void *)0x1;
      param_2 = (void *)CTexture__Helper_00567505(uVar2,(int)&param_1,1);
    }
    else {
      iVar4 = *(int *)((int)pvVar3 + 8);
      pvVar6 = (void *)(*(int *)pvVar3 - iVar4);
      *(int *)pvVar3 = iVar4 + 1;
      *(int *)((int)pvVar3 + 4) = *(int *)((int)pvVar3 + 0x18) + -1;
      if ((int)pvVar6 < 1) {
        if (uVar2 == 0xffffffff) {
          puVar5 = &DAT_00656080;
        }
        else {
          puVar5 = (undefined *)((&DAT_009d32a0)[(int)uVar2 >> 5] + (uVar2 & 0x1f) * 0x24);
        }
        if ((puVar5[4] & 0x20) != 0) {
          CRT__LseekFd(uVar2,0,2);
        }
      }
      else {
        param_2 = (void *)CTexture__Helper_00567505(uVar2,iVar4,(int)pvVar6);
      }
      **(undefined1 **)((int)pvVar3 + 8) = (undefined1)param_1;
    }
    if (param_2 == pvVar6) {
      return param_1 & 0xff;
    }
    *(uint *)((int)pvVar3 + 0xc) = *(uint *)((int)pvVar3 + 0xc) | 0x20;
  }
  return 0xffffffff;
}
