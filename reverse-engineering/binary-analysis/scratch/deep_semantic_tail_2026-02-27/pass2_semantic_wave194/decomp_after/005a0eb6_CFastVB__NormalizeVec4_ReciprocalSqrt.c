/* address: 0x005a0eb6 */
/* name: CFastVB__NormalizeVec4_ReciprocalSqrt */
/* signature: float * __stdcall CFastVB__NormalizeVec4_ReciprocalSqrt(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float * CFastVB__NormalizeVec4_ReciprocalSqrt(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined1 in_register_00001304 [12];
  float fVar6;
  undefined1 in_XMM5 [16];
  undefined1 auVar7 [16];
  undefined1 auVar8 [16];

  fVar1 = *(float *)param_2;
  fVar2 = *(float *)((int)param_2 + 4);
  fVar3 = *(float *)((int)param_2 + 8);
  fVar4 = *(float *)((int)param_2 + 0xc);
  auVar7._4_12_ = in_XMM5._4_12_;
  auVar7._0_4_ = fVar2 * fVar2;
  fVar5 = fVar1 * fVar1 + auVar7._0_4_ + fVar3 * fVar3 + fVar4 * fVar4;
  auVar8._4_12_ = in_register_00001304;
  auVar8._0_4_ = fVar5;
  auVar8 = rsqrtss(auVar7,auVar8);
  fVar6 = auVar8._0_4_;
  fVar6 = (DAT_0065e620 - fVar5 * fVar6 * fVar6) * _DAT_0065e610 * fVar6;
  *(float *)param_1 = fVar1 * fVar6;
  *(float *)((int)param_1 + 4) = fVar2 * fVar6;
  *(float *)((int)param_1 + 8) = fVar3 * fVar6;
  *(float *)((int)param_1 + 0xc) = fVar4 * fVar6;
  return param_1;
}
