/* address: 0x00411aa0 */
/* name: CMonitor__ComputeTerrainVelocityScalar */
/* signature: double __fastcall CMonitor__ComputeTerrainVelocityScalar(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CMonitor__ComputeTerrainVelocityScalar(int param_1)

{
  float fVar1;
  float fVar2;
  float *pfVar3;
  int *piVar4;
  double dVar5;
  undefined1 local_10 [16];

  fVar2 = DAT_006fbdfc;
  dVar5 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(*(int *)(param_1 + 0x18) + 0x1c));
  fVar1 = (float)dVar5;
  if (fVar1 <= fVar2) {
    piVar4 = *(int **)(param_1 + 0x18);
  }
  else {
    piVar4 = *(int **)(param_1 + 0x18);
    fVar1 = fVar2;
  }
  if (_DAT_005d8568 <= fVar1 - (float)piVar4[9]) {
    if (_DAT_005d8cc0 <= fVar1 - (float)piVar4[9]) {
      return (double)_DAT_005d8b9c;
    }
    pfVar3 = (float *)(**(code **)(*piVar4 + 0x6c))();
    if (SQRT(pfVar3[2] * pfVar3[2] + pfVar3[1] * pfVar3[1] + *pfVar3 * *pfVar3) < _DAT_005d8bd8) {
      return (double)(_DAT_005d8568 - (float)local_10 * _DAT_005d8574);
    }
  }
  return (double)_DAT_005d8cc4;
}
