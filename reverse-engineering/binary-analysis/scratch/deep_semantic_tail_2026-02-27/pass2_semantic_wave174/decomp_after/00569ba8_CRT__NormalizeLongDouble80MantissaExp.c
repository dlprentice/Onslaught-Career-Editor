/* address: 0x00569ba8 */
/* name: CRT__NormalizeLongDouble80MantissaExp */
/* signature: void __cdecl CRT__NormalizeLongDouble80MantissaExp(void * param_1, void * param_2) */


void __cdecl CRT__NormalizeLongDouble80MantissaExp(void *param_1,void *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint local_8;

  uVar1 = *(ushort *)((int)param_2 + 6);
  uVar4 = (uVar1 & 0x7ff0) >> 4;
  uVar2 = *(uint *)param_2;
  uVar3 = *(uint *)((int)param_2 + 4) & 0xfffff;
  local_8 = 0x80000000;
  if (uVar4 == 0) {
    if ((uVar3 == 0) && (uVar2 == 0)) {
      *(undefined4 *)((int)param_1 + 4) = 0;
      *(undefined4 *)param_1 = 0;
      *(undefined2 *)((int)param_1 + 8) = 0;
      return;
    }
    iVar5 = 0x3c01;
    local_8 = 0;
  }
  else if (uVar4 == 0x7ff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = uVar4 + 0x3c00;
  }
  local_8 = uVar2 >> 0x15 | uVar3 << 0xb | local_8;
  *(uint *)((int)param_1 + 4) = local_8;
  *(uint *)param_1 = uVar2 << 0xb;
  while ((local_8 & 0x80000000) == 0) {
    local_8 = *(uint *)param_1 >> 0x1f | local_8 * 2;
    *(uint *)param_1 = *(uint *)param_1 * 2;
    *(uint *)((int)param_1 + 4) = local_8;
    iVar5 = iVar5 + 0xffff;
  }
  *(ushort *)((int)param_1 + 8) = uVar1 & 0x8000 | (ushort)iVar5;
  return;
}
