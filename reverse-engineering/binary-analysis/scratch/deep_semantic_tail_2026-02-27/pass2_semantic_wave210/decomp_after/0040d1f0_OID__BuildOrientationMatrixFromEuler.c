/* address: 0x0040d1f0 */
/* name: OID__BuildOrientationMatrixFromEuler */
/* signature: void __thiscall OID__BuildOrientationMatrixFromEuler(void * this, void * param_1, float param_2, float param_3, float param_4) */


void __thiscall
OID__BuildOrientationMatrixFromEuler
          (void *this,void *param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float10 fVar5;
  float10 fVar6;

  fVar5 = (float10)fcos((float10)(float)param_1);
  fVar6 = (float10)fsin((float10)(float)param_1);
  fVar1 = (float)fVar6;
  fVar6 = (float10)fcos((float10)param_3);
  fVar2 = (float)fVar6;
  fVar6 = (float10)fsin((float10)param_3);
  fVar3 = (float)fVar6;
  fVar6 = (float10)fcos((float10)param_2);
  fVar4 = (float)fVar6;
  fVar6 = (float10)fsin((float10)param_2);
  *(float *)this = (float)((float10)fVar2 * fVar5 - fVar6 * (float10)fVar3 * (float10)fVar1);
  *(float *)((int)this + 4) = -(fVar4 * fVar1);
  *(float *)((int)this + 8) =
       (float)((float10)fVar3 * fVar5 + fVar6 * (float10)fVar2 * (float10)fVar1);
  *(float *)((int)this + 0x10) =
       (float)((float10)fVar2 * (float10)fVar1 + fVar6 * (float10)fVar3 * fVar5);
  *(float *)((int)this + 0x14) = (float)((float10)fVar4 * fVar5);
  *(float *)((int)this + 0x18) =
       (float)((float10)fVar3 * (float10)fVar1 - (float10)(float)(fVar6 * (float10)fVar2) * fVar5);
  *(float *)((int)this + 0x20) = -(fVar4 * fVar3);
  *(float *)((int)this + 0x24) = (float)fVar6;
  *(float *)((int)this + 0x28) = fVar4 * fVar2;
  return;
}
