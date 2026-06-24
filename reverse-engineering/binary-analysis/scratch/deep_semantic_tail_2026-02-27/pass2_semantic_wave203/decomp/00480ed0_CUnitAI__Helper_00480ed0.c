/* address: 0x00480ed0 */
/* name: CUnitAI__Helper_00480ed0 */
/* signature: void __thiscall CUnitAI__Helper_00480ed0(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnitAI__Helper_00480ed0(void *this,void *param_1,void *param_2)

{
  int *piVar1;
  void *re_use_event;
  float fVar2;
  void *data;
  void *unaff_EDI;
  float10 fVar3;
  float local_20;
  float local_1c;
  float local_18;
  float local_10;
  float local_c;
  float local_8;

  data = param_1;
  if ((*(int *)((int)this + 4) != 0) && (0x3b6 < *(int *)(*(int *)((int)this + 4) + 0xc))) {
    CConsole__Printf(&DAT_0066f580,s_WARNING__Object_colliding_with_t_0062ce20);
    return;
  }
  CUnitAI__Helper_004f3ac0(*(void **)((int)param_1 + 8),(int)&local_20,unaff_EDI);
  CUnitAI__Helper_004f3ac0(*(void **)(*(int *)((int)this + 8) + 8),(int)&local_10,unaff_EDI);
  param_1 = (void *)(local_18 - local_8);
  fVar2 = SQRT((local_20 - local_10) * (local_20 - local_10) +
               (float)param_1 * (float)param_1 + (local_1c - local_c) * (local_1c - local_c)) -
          (*(float *)(*(int *)((int)this + 8) + 0x1c) + *(float *)((int)data + 0x1c));
  if (_DAT_005d856c < fVar2) {
    piVar1 = *(int **)(*(int *)((int)this + 8) + 8);
    fVar3 = (float10)(**(code **)(**(int **)((int)data + 8) + 0x3c))();
    param_1 = (void *)(float)fVar3;
    fVar3 = (float10)(**(code **)(*piVar1 + 0x3c))();
    if (fVar3 + (float10)(float)param_1 == (float10)_DAT_005d856c) {
      return;
    }
    fVar3 = (float10)fVar2 / (fVar3 + (float10)(float)param_1) + (float10)DAT_00672fd0;
    if ((float10)DAT_00672fd0 < fVar3) {
      re_use_event = *(void **)((int)this + 0xc);
      param_1 = (void *)(float)fVar3;
      goto joined_r0x00480fc6;
    }
  }
  if (*(int *)((int)this + 0x10) == 0) {
    CHLCollisionDetector__HandleCollisionEnter(this,(int)data,unaff_EDI);
    return;
  }
  re_use_event = *(void **)((int)this + 0xc);
  param_1 = (void *)0xbf800000;
joined_r0x00480fc6:
  if (re_use_event != (void *)0x0) {
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,this,(float *)&param_1,1,data,re_use_event);
    *(undefined4 *)((int)this + 0xc) = 0;
    return;
  }
  CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,this,(float *)&param_1,1,data,(void *)0x0);
  return;
}
