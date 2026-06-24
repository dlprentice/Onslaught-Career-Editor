/* address: 0x004e83b0 */
/* name: CSquadNormal__Unk_004e83b0 */
/* signature: void __thiscall CSquadNormal__Unk_004e83b0(void * this, void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CSquadNormal__Unk_004e83b0(void *this,void *param_1,float param_2)

{
  undefined4 *puVar1;
  int *value;
  int iVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;

  puVar1 = *(undefined4 **)((int)this + 0xa4);
  if (puVar1 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*puVar1;
  }
  iVar2 = (**(code **)(*(int *)this + 0x124))();
  while (value = piVar5, value != (int *)0x0) {
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar1;
    }
    if ((*value == 0) || ((*(byte *)(*value + 0x2c) & 4) != 0)) {
      CSPtrSet__Remove((void *)((int)this + 0xa4),value);
      if (value != (int *)0x0) {
        CGenericActiveReader__dtor(value);
        OID__FreeObject(value);
      }
      *(int *)((int)this + 0xb4) = *(int *)((int)this + 0xb4) + -1;
      if (((*(int *)((int)this + 0xbc) != 2) || (*(int *)((int)this + 0x110) != 0)) ||
         ((iVar2 != 0 && (iVar3 = CSquadNormal__Helper_004fd570(iVar2), iVar3 != 0)))) {
        *(undefined4 *)((int)this + 0xbc) = 0;
      }
    }
  }
  CSquadNormal__Unk_004e84e0((int)this);
  if (param_1 != (void *)0x0) {
    uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar4 = uVar4 & 0x8000ffff;
    if ((int)uVar4 < 0) {
      uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
    }
    param_1 = (void *)((float)(int)uVar4 * _DAT_005d8d54 + _DAT_005d8568 + DAT_00672fd0);
    CEventManager__AddEvent_AtTime
              (&EVENT_MANAGER,0xfa1,this,(float *)&param_1,0,(void *)0x0,(void *)0x0);
  }
  return;
}
