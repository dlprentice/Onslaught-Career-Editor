/* address: 0x00579527 */
/* name: CTexture__Unk_00579527 */
/* signature: void __stdcall CTexture__Unk_00579527(void * param_1, void * param_2) */


void CTexture__Unk_00579527(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;

  CTexture__Helper_005780e3();
  fVar1 = local_c * *(float *)((int)param_2 + 8) +
          local_8 * *(float *)((int)param_2 + 0xc) +
          local_14 * *(float *)param_2 + local_10 * *(float *)((int)param_2 + 4);
  fVar4 = -local_14;
  fVar3 = -local_10;
  fVar2 = -local_c;
  fVar5 = -local_8;
  *(float *)param_1 = fVar4 * *(float *)param_2 + fVar1;
  *(float *)((int)param_1 + 0x10) = fVar3 * *(float *)param_2;
  *(float *)((int)param_1 + 0x20) = fVar2 * *(float *)param_2;
  *(float *)((int)param_1 + 0x30) = fVar5 * *(float *)param_2;
  *(float *)((int)param_1 + 4) = fVar4 * *(float *)((int)param_2 + 4);
  *(float *)((int)param_1 + 0x14) = fVar3 * *(float *)((int)param_2 + 4) + fVar1;
  *(float *)((int)param_1 + 0x24) = fVar2 * *(float *)((int)param_2 + 4);
  *(float *)((int)param_1 + 0x34) = fVar5 * *(float *)((int)param_2 + 4);
  *(float *)((int)param_1 + 8) = fVar4 * *(float *)((int)param_2 + 8);
  *(float *)((int)param_1 + 0x18) = fVar3 * *(float *)((int)param_2 + 8);
  *(float *)((int)param_1 + 0x28) = fVar2 * *(float *)((int)param_2 + 8) + fVar1;
  *(float *)((int)param_1 + 0x38) = fVar5 * *(float *)((int)param_2 + 8);
  *(float *)((int)param_1 + 0xc) = fVar4 * *(float *)((int)param_2 + 0xc);
  *(float *)((int)param_1 + 0x1c) = fVar3 * *(float *)((int)param_2 + 0xc);
  *(float *)((int)param_1 + 0x2c) = fVar2 * *(float *)((int)param_2 + 0xc);
  *(float *)((int)param_1 + 0x3c) = fVar5 * *(float *)((int)param_2 + 0xc) + fVar1;
  return;
}
