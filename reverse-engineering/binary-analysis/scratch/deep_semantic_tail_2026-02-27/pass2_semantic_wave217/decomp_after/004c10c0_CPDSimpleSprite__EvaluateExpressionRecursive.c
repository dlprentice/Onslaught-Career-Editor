/* address: 0x004c10c0 */
/* name: CPDSimpleSprite__EvaluateExpressionRecursive */
/* signature: double __thiscall CPDSimpleSprite__EvaluateExpressionRecursive(void * this, void * param_1, float param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
CPDSimpleSprite__EvaluateExpressionRecursive(void *this,void *param_1,float param_2,int param_3)

{
  void *pvVar1;
  void *pvVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  float fVar6;
  uint uVar7;
  int unaff_EDI;
  float10 fVar8;
  float10 fVar9;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float10 extraout_ST0_03;
  double dVar10;
  double dVar11;

  pvVar1 = param_1;
  iVar3 = *(int *)((int)this + 4);
  if (iVar3 == 0) {
    return (double)*(float *)this;
  }
  if (*(int *)(iVar3 + 0x84) != 0) {
    dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar3 + 0x88),DAT_009c6400,param_2,unaff_EDI);
    iVar4 = *(int *)(iVar3 + 0x80);
    uVar5 = *(undefined4 *)(iVar3 + 0x7c);
    CPDSimpleSprite__FpuDispatchStub();
    pvVar1 = (void *)(float)(extraout_ST0_01 / (float10)(float)dVar10);
    pvVar2 = (void *)(float)(extraout_ST0_01 / (float10)(float)dVar10);
    dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar3 + 100),pvVar1,param_2,unaff_EDI);
    dVar11 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar3 + 0x6c),pvVar1,param_2,unaff_EDI);
    param_1 = (void *)((float)dVar11 + (float)dVar10 * (float)pvVar1);
    switch(uVar5) {
    case 1:
      fVar9 = (float10)(float)param_1 * (float10)(float)param_1;
      break;
    case 2:
      fVar9 = ROUND((float10)1.4426950408889634 * (float10)(float)param_1);
      fVar8 = (float10)f2xm1((float10)1.4426950408889634 * (float10)(float)param_1 - fVar9);
      fVar9 = (float10)fscale((float10)1 + fVar8,fVar9);
      break;
    case 3:
      fVar9 = (float10)fsin((float10)(float)param_1);
      break;
    case 4:
      fVar9 = (float10)fcos((float10)(float)param_1);
      break;
    case 5:
      if ((float)param_1 == _DAT_005d856c) goto switchD_004c132e_caseD_7;
      fVar9 = (float10)_DAT_005d8568 / (float10)(float)param_1;
      break;
    case 6:
      fVar9 = (float10)0.6931471805599453 * (float10)(float)param_1;
      break;
    default:
      goto switchD_004c132e_caseD_7;
    case 10:
      uVar7 = _rand();
      fVar9 = (float10)(int)((uVar7 & 0xff) - 0x80) * (float10)_DAT_005ddac8;
    }
    param_1 = (void *)(float)fVar9;
switchD_004c132e_caseD_7:
    dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar3 + 0x5c),pvVar2,param_2,unaff_EDI);
    dVar11 = CPDSimpleSprite__EvaluateExpressionRecursive
                       ((void *)(iVar3 + 0x74),pvVar2,param_2,unaff_EDI);
    fVar6 = (float)dVar11 + (float)dVar10 * (float)param_1;
    if (iVar4 == 0) {
      if (_DAT_005d8568 < fVar6) {
        return (double)(_DAT_005d8568 * *(float *)this);
      }
      if (fVar6 < _DAT_005d8be0) {
        fVar6 = _DAT_005d8be0;
      }
    }
    else if (iVar4 == 1) {
      if (_DAT_005d8be0 < fVar6) {
        CPDSimpleSprite__FpuDispatchStub();
        return (double)((extraout_ST0_02 - (float10)_DAT_005d8568) * (float10)*(float *)this);
      }
      CPDSimpleSprite__FpuDispatchStub();
      return (double)(-(extraout_ST0_03 - (float10)_DAT_005d8568) * (float10)*(float *)this);
    }
    return (double)(fVar6 * *(float *)this);
  }
  iVar4 = *(int *)(iVar3 + 0x80);
  uVar5 = *(undefined4 *)(iVar3 + 0x7c);
  dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar3 + 100),param_1,param_2,unaff_EDI);
  dVar11 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar3 + 0x6c),param_1,param_2,unaff_EDI);
  param_1 = (void *)((float)dVar11 + (float)dVar10 * (float)param_1);
  switch(uVar5) {
  case 1:
    fVar9 = (float10)(float)param_1 * (float10)(float)param_1;
    break;
  case 2:
    fVar9 = ROUND((float10)1.4426950408889634 * (float10)(float)param_1);
    fVar8 = (float10)f2xm1((float10)1.4426950408889634 * (float10)(float)param_1 - fVar9);
    fVar9 = (float10)fscale((float10)1 + fVar8,fVar9);
    break;
  case 3:
    fVar9 = (float10)fsin((float10)(float)param_1);
    break;
  case 4:
    fVar9 = (float10)fcos((float10)(float)param_1);
    break;
  case 5:
    if ((float)param_1 == _DAT_005d856c) goto switchD_004c1131_caseD_7;
    fVar9 = (float10)_DAT_005d8568 / (float10)(float)param_1;
    break;
  case 6:
    fVar9 = (float10)0.6931471805599453 * (float10)(float)param_1;
    break;
  default:
    goto switchD_004c1131_caseD_7;
  case 10:
    uVar7 = _rand();
    fVar9 = (float10)(int)((uVar7 & 0xff) - 0x80) * (float10)_DAT_005ddac8;
  }
  param_1 = (void *)(float)fVar9;
switchD_004c1131_caseD_7:
  dVar10 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar3 + 0x5c),pvVar1,param_2,unaff_EDI);
  dVar11 = CPDSimpleSprite__EvaluateExpressionRecursive
                     ((void *)(iVar3 + 0x74),pvVar1,param_2,unaff_EDI);
  fVar6 = (float)dVar11 + (float)dVar10 * (float)param_1;
  if (iVar4 == 0) {
    if (_DAT_005d8568 < fVar6) {
      return (double)(_DAT_005d8568 * *(float *)this);
    }
    if (fVar6 < _DAT_005d8be0) {
      fVar6 = _DAT_005d8be0;
    }
  }
  else if (iVar4 == 1) {
    if (_DAT_005d8be0 < fVar6) {
      CPDSimpleSprite__FpuDispatchStub();
      return (double)((extraout_ST0 - (float10)_DAT_005d8568) * (float10)*(float *)this);
    }
    CPDSimpleSprite__FpuDispatchStub();
    return (double)(-(extraout_ST0_00 - (float10)_DAT_005d8568) * (float10)*(float *)this);
  }
  return (double)(fVar6 * *(float *)this);
}
