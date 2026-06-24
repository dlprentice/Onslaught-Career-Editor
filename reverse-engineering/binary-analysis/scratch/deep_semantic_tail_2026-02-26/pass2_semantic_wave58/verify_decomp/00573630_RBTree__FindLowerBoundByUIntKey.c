/* address: 0x00573630 */
/* name: RBTree__FindLowerBoundByUIntKey */
/* signature: void __thiscall RBTree__FindLowerBoundByUIntKey(void * this, int param_1, void * param_2, void * param_3) */


void __thiscall RBTree__FindLowerBoundByUIntKey(void *this,int param_1,void *param_2,void *param_3)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;

  puVar1 = *(undefined4 **)((int)this + 4);
  puVar4 = puVar1;
  if ((undefined4 *)puVar1[1] != DAT_009d0c44) {
    puVar2 = (undefined4 *)puVar1[1];
    do {
      if ((uint)puVar2[3] < *(uint *)param_2) {
        puVar3 = (undefined4 *)puVar2[2];
      }
      else {
        puVar3 = (undefined4 *)*puVar2;
        puVar4 = puVar2;
      }
      puVar2 = puVar3;
    } while (puVar3 != DAT_009d0c44);
  }
  if ((puVar4 != puVar1) && ((uint)puVar4[3] <= *(uint *)param_2)) {
    *(undefined4 **)param_1 = puVar4;
    return;
  }
  *(undefined4 **)param_1 = puVar1;
  return;
}
