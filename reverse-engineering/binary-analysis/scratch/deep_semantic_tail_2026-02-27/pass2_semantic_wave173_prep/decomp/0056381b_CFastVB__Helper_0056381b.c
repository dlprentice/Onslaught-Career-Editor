/* address: 0x0056381b */
/* name: CFastVB__Helper_0056381b */
/* signature: int __cdecl CFastVB__Helper_0056381b(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CFastVB__Helper_0056381b(void *param_1)

{
  undefined4 uVar1;
  int iVar2;
  void *pvVar3;

  iVar2 = CRT__IsFdCommitMode(*(uint *)((int)param_1 + 0x10));
  if (iVar2 == 0) {
    return 0;
  }
  if (param_1 == &DAT_006533e0) {
    iVar2 = 0;
  }
  else {
    if (param_1 != &DAT_00653400) {
      return 0;
    }
    iVar2 = 1;
  }
  _DAT_009d0908 = _DAT_009d0908 + 1;
  if ((*(ushort *)((int)param_1 + 0xc) & 0x10c) != 0) {
    return 0;
  }
  if ((&DAT_009d0978)[iVar2] == 0) {
    pvVar3 = _malloc(0x1000);
    (&DAT_009d0978)[iVar2] = pvVar3;
    if (pvVar3 == (void *)0x0) {
      *(int *)((int)param_1 + 8) = (int)param_1 + 0x14;
      *(int *)param_1 = (int)param_1 + 0x14;
      *(undefined4 *)((int)param_1 + 0x18) = 2;
      *(undefined4 *)((int)param_1 + 4) = 2;
      goto LAB_00563897;
    }
  }
  uVar1 = (&DAT_009d0978)[iVar2];
  *(undefined4 *)((int)param_1 + 0x18) = 0x1000;
  *(undefined4 *)((int)param_1 + 8) = uVar1;
  *(undefined4 *)param_1 = uVar1;
  *(undefined4 *)((int)param_1 + 4) = 0x1000;
LAB_00563897:
  *(ushort *)((int)param_1 + 0xc) = *(ushort *)((int)param_1 + 0xc) | 0x1102;
  return 1;
}
