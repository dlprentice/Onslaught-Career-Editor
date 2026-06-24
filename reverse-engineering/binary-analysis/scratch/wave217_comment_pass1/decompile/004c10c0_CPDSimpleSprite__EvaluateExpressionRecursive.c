/* address: 0x004c10c0 */
/* name: CPDSimpleSprite__EvaluateExpressionRecursive */
/* signature: double __thiscall CPDSimpleSprite__EvaluateExpressionRecursive(void * this, void * x_value, float time_scale, int eval_flags) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Evaluates simple-sprite expression tree recursively and returns scalar result (double).
   Used by particle/simple-sprite runtime math dispatch. */

double __thiscall
CPDSimpleSprite__EvaluateExpressionRecursive
          (void *this,void *x_value,float time_scale,int eval_flags)

{
  void *pvVar1;
  void *x_value_00;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  float fVar5;
  uint uVar6;
  int unaff_EDI;
  float10 fVar7;
  float10 fVar8;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float10 extraout_ST0_03;
  double dVar9;
  double dVar10;

  pvVar1 = x_value;
  iVar2 = *(int *)((int)this + 4);
  if (iVar2 == 0) {
    return (double)*(float *)this;
  }
  if (*(int *)(iVar2 + 0x84) != 0) {
    dVar9 = CPDSimpleSprite__EvaluateExpressionRecursive
                      ((void *)(iVar2 + 0x88),DAT_009c6400,time_scale,unaff_EDI);
    iVar3 = *(int *)(iVar2 + 0x80);
    uVar4 = *(undefined4 *)(iVar2 + 0x7c);
    CPDSimpleSprite__FpuDispatchStub();
    pvVar1 = (void *)(float)(extraout_ST0_01 / (float10)(float)dVar9);
    x_value_00 = (void *)(float)(extraout_ST0_01 / (float10)(float)dVar9);
    dVar9 = CPDSimpleSprite__EvaluateExpressionRecursive
                      ((void *)(iVar2 + 100),pvVar1,time_scale,unaff_EDI);
    dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar2 + 0x6c),pvVar1,time_scale,unaff_EDI);
    x_value = (void *)((float)dVar10 + (float)dVar9 * (float)pvVar1);
    switch(uVar4) {
    case 1:
      fVar8 = (float10)(float)x_value * (float10)(float)x_value;
      break;
    case 2:
      fVar8 = ROUND((float10)1.4426950408889634 * (float10)(float)x_value);
      fVar7 = (float10)f2xm1((float10)1.4426950408889634 * (float10)(float)x_value - fVar8);
      fVar8 = (float10)fscale((float10)1 + fVar7,fVar8);
      break;
    case 3:
      fVar8 = (float10)fsin((float10)(float)x_value);
      break;
    case 4:
      fVar8 = (float10)fcos((float10)(float)x_value);
      break;
    case 5:
      if ((float)x_value == _DAT_005d856c) goto switchD_004c132e_caseD_7;
      fVar8 = (float10)_DAT_005d8568 / (float10)(float)x_value;
      break;
    case 6:
      fVar8 = (float10)0.6931471805599453 * (float10)(float)x_value;
      break;
    default:
      goto switchD_004c132e_caseD_7;
    case 10:
      uVar6 = _rand();
      fVar8 = (float10)(int)((uVar6 & 0xff) - 0x80) * (float10)_DAT_005ddac8;
    }
    x_value = (void *)(float)fVar8;
switchD_004c132e_caseD_7:
    dVar9 = CPDSimpleSprite__EvaluateExpressionRecursive
                      ((void *)(iVar2 + 0x5c),x_value_00,time_scale,unaff_EDI);
    dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar2 + 0x74),x_value_00,time_scale,unaff_EDI);
    fVar5 = (float)dVar10 + (float)dVar9 * (float)x_value;
    if (iVar3 == 0) {
      if (_DAT_005d8568 < fVar5) {
        return (double)(_DAT_005d8568 * *(float *)this);
      }
      if (fVar5 < _DAT_005d8be0) {
        fVar5 = _DAT_005d8be0;
      }
    }
    else if (iVar3 == 1) {
      if (_DAT_005d8be0 < fVar5) {
        CPDSimpleSprite__FpuDispatchStub();
        return (double)((extraout_ST0_02 - (float10)_DAT_005d8568) * (float10)*(float *)this);
      }
      CPDSimpleSprite__FpuDispatchStub();
      return (double)(-(extraout_ST0_03 - (float10)_DAT_005d8568) * (float10)*(float *)this);
    }
    return (double)(fVar5 * *(float *)this);
  }
  iVar3 = *(int *)(iVar2 + 0x80);
  uVar4 = *(undefined4 *)(iVar2 + 0x7c);
  dVar9 = CPDSimpleSprite__EvaluateExpressionRecursive
                    ((void *)(iVar2 + 100),x_value,time_scale,unaff_EDI);
  dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar2 + 0x6c),x_value,time_scale,unaff_EDI);
  x_value = (void *)((float)dVar10 + (float)dVar9 * (float)x_value);
  switch(uVar4) {
  case 1:
    fVar8 = (float10)(float)x_value * (float10)(float)x_value;
    break;
  case 2:
    fVar8 = ROUND((float10)1.4426950408889634 * (float10)(float)x_value);
    fVar7 = (float10)f2xm1((float10)1.4426950408889634 * (float10)(float)x_value - fVar8);
    fVar8 = (float10)fscale((float10)1 + fVar7,fVar8);
    break;
  case 3:
    fVar8 = (float10)fsin((float10)(float)x_value);
    break;
  case 4:
    fVar8 = (float10)fcos((float10)(float)x_value);
    break;
  case 5:
    if ((float)x_value == _DAT_005d856c) goto switchD_004c1131_caseD_7;
    fVar8 = (float10)_DAT_005d8568 / (float10)(float)x_value;
    break;
  case 6:
    fVar8 = (float10)0.6931471805599453 * (float10)(float)x_value;
    break;
  default:
    goto switchD_004c1131_caseD_7;
  case 10:
    uVar6 = _rand();
    fVar8 = (float10)(int)((uVar6 & 0xff) - 0x80) * (float10)_DAT_005ddac8;
  }
  x_value = (void *)(float)fVar8;
switchD_004c1131_caseD_7:
  dVar9 = CPDSimpleSprite__EvaluateExpressionRecursive
                    ((void *)(iVar2 + 0x5c),pvVar1,time_scale,unaff_EDI);
  dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar2 + 0x74),pvVar1,time_scale,unaff_EDI);
  fVar5 = (float)dVar10 + (float)dVar9 * (float)x_value;
  if (iVar3 == 0) {
    if (_DAT_005d8568 < fVar5) {
      return (double)(_DAT_005d8568 * *(float *)this);
    }
    if (fVar5 < _DAT_005d8be0) {
      fVar5 = _DAT_005d8be0;
    }
  }
  else if (iVar3 == 1) {
    if (_DAT_005d8be0 < fVar5) {
      CPDSimpleSprite__FpuDispatchStub();
      return (double)((extraout_ST0 - (float10)_DAT_005d8568) * (float10)*(float *)this);
    }
    CPDSimpleSprite__FpuDispatchStub();
    return (double)(-(extraout_ST0_00 - (float10)_DAT_005d8568) * (float10)*(float *)this);
  }
  return (double)(fVar5 * *(float *)this);
}
