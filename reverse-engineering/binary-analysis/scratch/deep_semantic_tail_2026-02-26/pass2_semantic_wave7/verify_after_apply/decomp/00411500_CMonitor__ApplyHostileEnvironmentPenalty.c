/* address: 0x00411500 */
/* name: CMonitor__ApplyHostileEnvironmentPenalty */
/* signature: void __fastcall CMonitor__ApplyHostileEnvironmentPenalty(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__ApplyHostileEnvironmentPenalty(int param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  double dVar4;
  undefined4 local_10;
  undefined4 local_c;
  float local_8;
  undefined4 local_4;

  fVar2 = DAT_006fbdfc;
  iVar1 = *(int *)(param_1 + 0x18);
  local_10 = *(undefined4 *)(iVar1 + 0x1c);
  local_c = *(undefined4 *)(iVar1 + 0x20);
  local_8 = *(float *)(iVar1 + 0x24);
  local_4 = *(undefined4 *)(iVar1 + 0x28);
  dVar4 = CStaticShadows__Helper_0047eb80(0x6fadc8,&local_10);
  if (((double)fVar2 < dVar4) && (fVar2 = fVar2 - local_8, fVar2 < _DAT_005d85ec)) {
    iVar1 = *(int *)(param_1 + 0x18);
    fVar3 = SQRT(*(float *)(iVar1 + 0x80) * *(float *)(iVar1 + 0x80) +
                 *(float *)(iVar1 + 0x7c) * *(float *)(iVar1 + 0x7c));
    if (_DAT_005d8cb4 < fVar3) {
      *(float *)(iVar1 + 0x84) = *(float *)(iVar1 + 0x84) - fVar3 * _DAT_005d8cb4;
      *(float *)(*(int *)(param_1 + 0x18) + 0x280) =
           *(float *)(*(int *)(param_1 + 0x18) + 0x280) - fVar3 * _DAT_005d8574;
      iVar1 = *(int *)(param_1 + 0x18);
      *(float *)(iVar1 + 0x7c) = *(float *)(iVar1 + 0x7c) * _DAT_005d85f8;
      *(float *)(iVar1 + 0x80) = *(float *)(iVar1 + 0x80) * _DAT_005d85f8;
      *(float *)(iVar1 + 0x84) = *(float *)(iVar1 + 0x84) * _DAT_005d85f8;
      (**(code **)(**(int **)(param_1 + 0x18) + 0xa0))
                ((_DAT_005d85ec - fVar2) * _DAT_005d857c,0,0,0xffffffff);
      CBattleEngine__HostileEnvironment(*(int *)(param_1 + 0x18));
      return;
    }
  }
  return;
}
