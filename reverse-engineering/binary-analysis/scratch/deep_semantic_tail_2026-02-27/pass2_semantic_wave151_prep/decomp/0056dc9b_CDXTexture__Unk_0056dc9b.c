/* address: 0x0056dc9b */
/* name: CDXTexture__Unk_0056dc9b */
/* signature: uint __cdecl CDXTexture__Unk_0056dc9b(uint param_1, void * param_2) */


uint __cdecl CDXTexture__Unk_0056dc9b(uint param_1,void *param_2)

{
  uint uVar1;
  void *pvVar2;
  int iVar3;
  undefined *puVar4;
  uint uVar5;
  void *pvVar6;

  pvVar2 = param_2;
  uVar5 = *(uint *)((int)param_2 + 0xc);
  uVar1 = *(uint *)((int)param_2 + 0x10);
  if (((uVar5 & 0x82) == 0) || ((uVar5 & 0x40) != 0)) {
LAB_0056ddb4:
    *(uint *)((int)param_2 + 0xc) = uVar5 | 0x20;
  }
  else {
    if ((uVar5 & 1) != 0) {
      *(undefined4 *)((int)param_2 + 4) = 0;
      if ((uVar5 & 0x10) == 0) goto LAB_0056ddb4;
      *(undefined4 *)param_2 = *(undefined4 *)((int)param_2 + 8);
      *(uint *)((int)param_2 + 0xc) = uVar5 & 0xfffffffe;
    }
    uVar5 = *(uint *)((int)param_2 + 0xc);
    *(undefined4 *)((int)param_2 + 4) = 0;
    param_2 = (void *)0x0;
    *(uint *)((int)pvVar2 + 0xc) = uVar5 & 0xffffffef | 2;
    if (((uVar5 & 0x10c) == 0) &&
       (((pvVar2 != &DAT_006533e0 && (pvVar2 != &DAT_00653400)) ||
        (iVar3 = CDXTexture__Unk_00569dd5(uVar1), iVar3 == 0)))) {
      CDXTexture__Unk_00569d91(pvVar2);
    }
    uVar5 = param_1;
    if ((*(ushort *)((int)pvVar2 + 0xc) & 0x108) == 0) {
      pvVar6 = (void *)0x2;
      param_2 = (void *)CTexture__Helper_00567505(uVar1,(int)&param_1,2);
    }
    else {
      iVar3 = *(int *)((int)pvVar2 + 8);
      pvVar6 = (void *)(*(int *)pvVar2 - iVar3);
      *(int *)pvVar2 = iVar3 + 2;
      *(int *)((int)pvVar2 + 4) = *(int *)((int)pvVar2 + 0x18) + -2;
      if ((int)pvVar6 < 1) {
        if (uVar1 == 0xffffffff) {
          puVar4 = &DAT_00656080;
        }
        else {
          puVar4 = (undefined *)((&DAT_009d32a0)[(int)uVar1 >> 5] + (uVar1 & 0x1f) * 0x24);
        }
        if ((puVar4[4] & 0x20) != 0) {
          CRT__LseekFd(uVar1,0,2);
        }
      }
      else {
        param_2 = (void *)CTexture__Helper_00567505(uVar1,iVar3,(int)pvVar6);
      }
      **(undefined2 **)((int)pvVar2 + 8) = (short)param_1;
      uVar5 = param_1;
    }
    if (param_2 == pvVar6) {
      return uVar5 & 0xffff;
    }
    *(uint *)((int)pvVar2 + 0xc) = *(uint *)((int)pvVar2 + 0xc) | 0x20;
  }
  return 0xffff;
}
