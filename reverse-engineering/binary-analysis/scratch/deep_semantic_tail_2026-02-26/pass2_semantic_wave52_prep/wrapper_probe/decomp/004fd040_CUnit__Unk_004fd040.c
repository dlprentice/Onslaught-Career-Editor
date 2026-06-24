/* address: 0x004fd040 */
/* name: CUnit__Unk_004fd040 */
/* signature: void __fastcall CUnit__Unk_004fd040(void * param_1) */


void __fastcall CUnit__Unk_004fd040(void *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  int *piVar3;
  float10 fVar4;
  float local_8;
  void *local_4;

  local_4 = (void *)((int)param_1 + 0x19c);
  piVar3 = (int *)LinkedPtrCursor__MoveFirstAndGet(&local_8);
  while (piVar3 != (int *)0x0) {
    piVar1 = (int *)*piVar3;
    if (piVar1 != (int *)0x0) {
      if ((*(byte *)((int)param_1 + 0x2c) & 4) == 0) {
        (**(code **)(*piVar1 + 8))();
      }
      else {
        (**(code **)(*piVar1 + 200))();
      }
    }
    CSPtrSet__Remove((void *)((int)param_1 + 0x19c),piVar3);
    if (piVar3 != (int *)0x0) {
      CGenericActiveReader__dtor(piVar3);
      OID__FreeObject(piVar3);
    }
    piVar3 = (int *)LinkedPtrCursor__MoveFirstAndGet(&local_8);
  }
  CGenericActiveReader__SetReader((void *)((int)param_1 + 0x144),(void *)0x0);
  while ((puVar2 = *(undefined4 **)((int)param_1 + 0x18c), puVar2 != (undefined4 *)0x0 &&
         (piVar3 = (int *)*puVar2, piVar3 != (int *)0x0))) {
    CSPtrSet__Remove((int *)((int)param_1 + 0x18c),piVar3);
    (**(code **)(*piVar3 + 8))();
  }
  CExplosionInitThing__ctor_like_004fd230(param_1);
  if (*(int *)((int)param_1 + 0x74) != 0) {
    IScript__Unk_005337e0(*(int *)((int)param_1 + 0x74));
    if (*(int **)((int)param_1 + 0x74) != (int *)0x0) {
      (**(code **)(**(int **)((int)param_1 + 0x74) + 4))(1);
    }
    *(undefined4 *)((int)param_1 + 0x74) = 0;
  }
  fVar4 = (float10)(**(code **)(*(int *)param_1 + 0x1c0))();
  local_8 = (float)(fVar4 + (float10)DAT_00672fd0);
  CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,param_1,&local_8,0,(void *)0x0,(void *)0x0);
  return;
}
