/* address: 0x004e8f80 */
/* name: CSquadNormal__Unk_004e8f80 */
/* signature: void __thiscall CSquadNormal__Unk_004e8f80(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CSquadNormal__Unk_004e8f80(void *this,void *param_1,int param_2)

{
  undefined4 *puVar1;
  float fVar2;
  float fVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  undefined1 local_10 [4];
  int *local_c;

  if (((((*(int *)((int)this + 0xc4) == 0) && (_DAT_005d856c < *(float *)((int)this + 0x10c))) &&
       (*(int *)((int)this + 0x84) == 0)) &&
      ((*(int *)((int)this + 0x114) != 0 && (*(int *)((int)this + 0x80) == 0)))) &&
     ((*(byte *)((int)this + 0x2c) & 1) == 0)) {
    local_c = (int *)((int)this + 0xa4);
    piVar4 = (int *)LinkedPtrCursor__MoveFirstAndGet(local_10);
    while (piVar4 != (int *)0x0) {
      if (((int *)*piVar4 != (int *)0x0) &&
         (iVar5 = (**(code **)(*(int *)*piVar4 + 0x10c))(), iVar5 == 0)) {
        return;
      }
      piVar4 = (int *)LinkedPtrCursor__MoveNextAndGet(local_10);
    }
    if ((*(int *)((int)this + 0xb4) < *(int *)((int)this + 0xb8)) || (param_1 != (void *)0x0)) {
      puVar1 = DAT_008550a0;
      if (DAT_008550a0 == (undefined4 *)0x0) {
        piVar4 = (int *)0x0;
      }
      else {
        piVar4 = (int *)*DAT_008550a0;
      }
      while (piVar4 != (int *)0x0) {
        if ((((((piVar4[0x1f] == *(int *)((int)this + 0x7c)) &&
               (iVar5 = (**(code **)(*piVar4 + 0x14c))(), iVar5 == 0)) &&
              (fVar2 = *(float *)((int)this + 0x1c) - (float)piVar4[7],
              fVar3 = *(float *)((int)this + 0x20) - (float)piVar4[8],
              SQRT(fVar2 * fVar2 + fVar3 * fVar3) < _DAT_005d8610)) &&
             (((piVar4 != this && (piVar4[0x28] == *(int *)((int)this + 0xa0))) &&
              ((piVar4[0x27] == *(int *)((int)this + 0x9c) &&
               ((_DAT_005d856c < (float)piVar4[0x43] && (piVar4[0x21] == 0)))))))) &&
            (piVar4[0x45] != 0)) && ((piVar4[0x20] == 0 && ((*(byte *)(piVar4 + 0xb) & 1) == 0)))) {
          local_c = piVar4 + 0x29;
          piVar6 = (int *)LinkedPtrCursor__MoveFirstAndGet(local_10);
          while (piVar6 != (int *)0x0) {
            if (((int *)*piVar6 != (int *)0x0) &&
               (iVar5 = (**(code **)(*(int *)*piVar6 + 0x10c))(), iVar5 == 0)) goto LAB_004e915a;
            piVar6 = (int *)LinkedPtrCursor__MoveNextAndGet(local_10);
          }
          if ((piVar4[0x2c] + *(int *)((int)this + 0xb4) <= *(int *)((int)this + 0xb8)) ||
             (param_1 != (void *)0x0)) {
            while( true ) {
              puVar1 = *(undefined4 **)((int)this + 0xa4);
              *(undefined4 **)((int)this + 0xac) = puVar1;
              if (puVar1 == (undefined4 *)0x0) {
                return;
              }
              piVar6 = (int *)*puVar1;
              if (piVar6 == (int *)0x0) break;
              iVar5 = *piVar6;
              if (iVar5 == 0) {
                CSPtrSet__Remove((void *)((int)this + 0xa4),piVar6);
                CGenericActiveReader__dtor(piVar6);
                OID__FreeObject(piVar6);
                piVar4[0x2f] = 0;
              }
              else {
                CSquadNormal__RemoveMember(iVar5);
                (**(code **)(*piVar4 + 0x10c))(local_10,iVar5,0,0);
                piVar4[0x2f] = 0;
              }
            }
            return;
          }
        }
LAB_004e915a:
        puVar1 = (undefined4 *)puVar1[1];
        if (puVar1 == (undefined4 *)0x0) {
          piVar4 = (int *)0x0;
        }
        else {
          piVar4 = (int *)*puVar1;
        }
      }
    }
  }
  return;
}
