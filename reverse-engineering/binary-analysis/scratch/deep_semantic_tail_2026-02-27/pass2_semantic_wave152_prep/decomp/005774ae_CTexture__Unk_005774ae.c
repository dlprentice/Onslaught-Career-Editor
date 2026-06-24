/* address: 0x005774ae */
/* name: CTexture__Unk_005774ae */
/* signature: void __stdcall CTexture__Unk_005774ae(void * param_1, void * param_2, float param_3) */


void CTexture__Unk_005774ae(void *param_1,void *param_2,float param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float10 fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float10 fVar11;

  fVar6 = (float10)fcos((float10)param_3);
  fVar11 = (float10)fsin((float10)param_3);
  fVar1 = (float)fVar6;
  fVar2 = (float)fVar11;
  fVar7 = 1.0 - fVar1;
  fVar3 = *(float *)param_2;
  fVar4 = *(float *)((int)param_2 + 4);
  fVar5 = *(float *)((int)param_2 + 8);
  CTexture__Helper_00575d99();
  fVar8 = fVar4 * fVar3 * fVar7;
  fVar9 = fVar4 * fVar5 * fVar7;
  fVar10 = fVar5 * fVar3 * fVar7;
  *(float *)param_1 = fVar3 * fVar3 * fVar7 + fVar1;
  *(float *)((int)param_1 + 4) = fVar8 + fVar5 * fVar2;
  *(float *)((int)param_1 + 8) = fVar10 - fVar4 * fVar2;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(float *)((int)param_1 + 0x10) = fVar8 - fVar5 * fVar2;
  *(float *)((int)param_1 + 0x14) = fVar4 * fVar4 * fVar7 + fVar1;
  *(float *)((int)param_1 + 0x18) = fVar3 * fVar2 + fVar9;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(float *)((int)param_1 + 0x20) = fVar4 * fVar2 + fVar10;
  *(float *)((int)param_1 + 0x24) = fVar9 - fVar3 * fVar2;
  *(float *)((int)param_1 + 0x28) = fVar5 * fVar5 * fVar7 + fVar1;
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  *(undefined4 *)((int)param_1 + 0x30) = 0;
  *(undefined4 *)((int)param_1 + 0x34) = 0;
  *(undefined4 *)((int)param_1 + 0x38) = 0;
  *(undefined4 *)((int)param_1 + 0x3c) = 0x3f800000;
  return;
}
