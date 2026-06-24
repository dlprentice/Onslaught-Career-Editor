/* address: 0x004ebe40 */
/* name: CStaticShadows__UpdateLightVectorAndRebuild */
/* signature: void __fastcall CStaticShadows__UpdateLightVectorAndRebuild(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CStaticShadows__UpdateLightVectorAndRebuild(int param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  undefined4 *puVar4;
  int *piVar5;

  *(float *)(param_1 + 8) = -_DAT_006fbe6c;
  *(float *)(param_1 + 0xc) = -DAT_006fbe70;
  fVar2 = -_DAT_006fbe74;
  *(float *)(param_1 + 0x10) = fVar2;
  fVar1 = SQRT(*(float *)(param_1 + 0xc) * *(float *)(param_1 + 0xc) +
               *(float *)(param_1 + 8) * *(float *)(param_1 + 8));
  if (fVar2 + fVar2 < fVar1) {
    *(float *)(param_1 + 8) = ((fVar2 + fVar2) / fVar1) * *(float *)(param_1 + 8);
    *(float *)(param_1 + 0xc) =
         ((*(float *)(param_1 + 0x10) + *(float *)(param_1 + 0x10)) / fVar1) *
         *(float *)(param_1 + 0xc);
  }
  fVar1 = SQRT(*(float *)(param_1 + 0x10) * *(float *)(param_1 + 0x10) +
               *(float *)(param_1 + 0xc) * *(float *)(param_1 + 0xc) +
               *(float *)(param_1 + 8) * *(float *)(param_1 + 8));
  if (fVar1 != _DAT_005d856c) {
    fVar1 = _DAT_005d8568 / fVar1;
    *(float *)(param_1 + 8) = fVar1 * *(float *)(param_1 + 8);
    *(float *)(param_1 + 0xc) = fVar1 * *(float *)(param_1 + 0xc);
    *(float *)(param_1 + 0x10) = fVar1 * *(float *)(param_1 + 0x10);
  }
  if (DAT_00662dc0 == 0) {
    DAT_00855098 = DAT_00855090;
    if (DAT_00855090 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*DAT_00855090;
    }
    while (piVar5 != (int *)0x0) {
      iVar3 = (**(code **)(*piVar5 + 0x28))();
      if ((iVar3 != 0) && (iVar3 = (**(code **)(*piVar5 + 0x2c))(), iVar3 == 0)) {
        puVar4 = (undefined4 *)
                 OID__AllocObject(0x24,0x70,s_C__dev_ONSLAUGHT2_StaticShadows__006329f8,0xc1);
        if (puVar4 == (undefined4 *)0x0) {
          puVar4 = (undefined4 *)0x0;
        }
        else {
          puVar4[8] = DAT_009c8010;
          DAT_009c8010 = puVar4;
          puVar4[2] = 0;
          puVar4[3] = 0;
          *puVar4 = 0;
        }
        *puVar4 = piVar5;
        puVar4[1] = 0xffffffff;
        (**(code **)(*piVar5 + 0x30))(puVar4);
        CStaticShadows__BuildShadowMaps();
      }
      DAT_00855098 = (undefined4 *)DAT_00855098[1];
      if (DAT_00855098 == (undefined4 *)0x0) {
        piVar5 = (int *)0x0;
      }
      else {
        piVar5 = (int *)*DAT_00855098;
      }
    }
  }
  return;
}
