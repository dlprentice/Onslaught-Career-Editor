/* address: 0x00567aba */
/* name: CFastVB__Helper_00567aba */
/* signature: uint __cdecl CFastVB__Helper_00567aba(void * param_1) */


uint __cdecl CFastVB__Helper_00567aba(void *param_1)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined *puVar4;

  uVar2 = *(uint *)((int)param_1 + 0xc);
  if (((uVar2 & 0x83) != 0) && ((uVar2 & 0x40) == 0)) {
    if ((uVar2 & 2) == 0) {
      *(uint *)((int)param_1 + 0xc) = uVar2 | 1;
      if ((uVar2 & 0x10c) == 0) {
        CRT__InitFileBuffer(param_1);
      }
      else {
        *(undefined4 *)param_1 = *(undefined4 *)((int)param_1 + 8);
      }
      iVar3 = CFastVB__Helper_00567b96
                        (*(uint *)((int)param_1 + 0x10),*(int *)((int)param_1 + 8),
                         *(int *)((int)param_1 + 0x18));
      *(int *)((int)param_1 + 4) = iVar3;
      if ((iVar3 != 0) && (iVar3 != -1)) {
        if ((*(uint *)((int)param_1 + 0xc) & 0x82) == 0) {
          uVar2 = *(uint *)((int)param_1 + 0x10);
          if (uVar2 == 0xffffffff) {
            puVar4 = &DAT_00656080;
          }
          else {
            puVar4 = (undefined *)((&DAT_009d32a0)[(int)uVar2 >> 5] + (uVar2 & 0x1f) * 0x24);
          }
          if ((puVar4[4] & 0x82) == 0x82) {
            *(uint *)((int)param_1 + 0xc) = *(uint *)((int)param_1 + 0xc) | 0x2000;
          }
        }
        if (((*(int *)((int)param_1 + 0x18) == 0x200) && ((*(uint *)((int)param_1 + 0xc) & 8) != 0))
           && ((*(uint *)((int)param_1 + 0xc) & 0x400) == 0)) {
          *(undefined4 *)((int)param_1 + 0x18) = 0x1000;
        }
        *(int *)((int)param_1 + 4) = iVar3 + -1;
        bVar1 = **(byte **)param_1;
        *(byte **)param_1 = *(byte **)param_1 + 1;
        return (uint)bVar1;
      }
      *(uint *)((int)param_1 + 0xc) =
           *(uint *)((int)param_1 + 0xc) | (-(uint)(iVar3 != 0) & 0x10) + 0x10;
      *(undefined4 *)((int)param_1 + 4) = 0;
    }
    else {
      *(uint *)((int)param_1 + 0xc) = uVar2 | 0x20;
    }
  }
  return 0xffffffff;
}
