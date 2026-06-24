/* address: 0x004db630 */
/* name: CEngine__Unk_004db630 */
/* signature: void __fastcall CEngine__Unk_004db630(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CEngine__Unk_004db630(int param_1)

{
  int iVar1;
  float fVar2;
  int iVar3;
  undefined4 *puVar4;
  int unaff_EDI;
  undefined4 *puVar5;

  if ((*(int *)(param_1 + 300) == 0) && (*(int *)(*(int *)(param_1 + 0xf0) + 0x6c) != 0)) {
    *(undefined4 *)(param_1 + 300) = 1;
    *(float *)(param_1 + 0x24) = DAT_006fbdfc - _DAT_005d8578;
    fVar2 = SQRT(*(float *)(param_1 + 0x84) * *(float *)(param_1 + 0x84) +
                 *(float *)(param_1 + 0x80) * *(float *)(param_1 + 0x80) +
                 *(float *)(param_1 + 0x7c) * *(float *)(param_1 + 0x7c));
    if (fVar2 != _DAT_005d856c) {
      fVar2 = _DAT_005d8568 / fVar2;
      *(float *)(param_1 + 0x7c) = fVar2 * *(float *)(param_1 + 0x7c);
      *(float *)(param_1 + 0x80) = fVar2 * *(float *)(param_1 + 0x80);
      *(float *)(param_1 + 0x84) = fVar2 * *(float *)(param_1 + 0x84);
    }
    *(undefined4 *)(param_1 + 0x84) = 0;
    fVar2 = *(float *)(*(int *)(param_1 + 0xf0) + 0x2c) * _DAT_005d8584;
    *(float *)(param_1 + 0x7c) = fVar2 * *(float *)(param_1 + 0x7c);
    *(float *)(param_1 + 0x80) = fVar2 * *(float *)(param_1 + 0x80);
    *(float *)(param_1 + 0x84) = fVar2 * *(float *)(param_1 + 0x84);
    CParticleManager__Unk_004cb0b0((void *)(param_1 + 0xe0),0,unaff_EDI);
    if (*(int *)(*(int *)(param_1 + 0xf0) + 4) != 0) {
      *(undefined4 *)(param_1 + 0xe4) = 0;
      CParticleManager__CreateEffect
                (*(undefined4 *)(*(int *)(param_1 + 0xf0) + 4),(void *)(param_1 + 0xe0),DAT_0083cc88
                 ,DAT_0083cc8c,DAT_0083cc90,DAT_0083cc94,0,0);
      puVar5 = *(undefined4 **)(param_1 + 0xe4);
      puVar4 = (undefined4 *)(param_1 + 0x1c);
      if (puVar5 != (undefined4 *)0x0) {
        if (puVar5[0x12] == 0x461c4000) {
          puVar5[0x20] = *puVar4;
          puVar5[0x21] = *(undefined4 *)(param_1 + 0x20);
          puVar5[0x22] = *(undefined4 *)(param_1 + 0x24);
          puVar5[0x23] = *(undefined4 *)(param_1 + 0x28);
          puVar5[0x10] = *puVar4;
          puVar5[0x11] = *(undefined4 *)(param_1 + 0x20);
          puVar5[0x12] = *(undefined4 *)(param_1 + 0x24);
          puVar5[0x13] = *(undefined4 *)(param_1 + 0x28);
          *puVar5 = *puVar4;
          puVar5[1] = *(undefined4 *)(param_1 + 0x20);
          puVar5[2] = *(undefined4 *)(param_1 + 0x24);
          puVar5[3] = *(undefined4 *)(param_1 + 0x28);
          iVar1 = puVar5[0x2b];
        }
        else {
          puVar5[0x10] = *puVar5;
          puVar5[0x11] = puVar5[1];
          puVar5[0x12] = puVar5[2];
          puVar5[0x13] = puVar5[3];
          *puVar5 = *puVar4;
          puVar5[1] = *(undefined4 *)(param_1 + 0x20);
          puVar5[2] = *(undefined4 *)(param_1 + 0x24);
          puVar5[3] = *(undefined4 *)(param_1 + 0x28);
          iVar1 = puVar5[0x2b];
        }
        if (iVar1 != -0x40800000) {
          puVar5[0x2b] = DAT_00672fd0;
        }
      }
      iVar1 = *(int *)(param_1 + 0xe4);
      if (iVar1 != 0) {
        puVar4 = (undefined4 *)(param_1 + 0x3c);
        puVar5 = (undefined4 *)(iVar1 + 0x10);
        for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
          *puVar5 = *puVar4;
          puVar4 = puVar4 + 1;
          puVar5 = puVar5 + 1;
        }
        *(undefined4 *)(iVar1 + 0xa0) = 1;
      }
    }
  }
  return;
}
