/* address: 0x00594836 */
/* name: CFastVB__Helper_00594836 */
/* signature: void __stdcall CFastVB__Helper_00594836(void * param_1, void * param_2, int param_3, int param_4) */


void CFastVB__Helper_00594836(void *param_1,void *param_2,int param_3,int param_4)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  undefined1 *puVar4;
  int iVar5;
  byte *pbVar6;
  byte *pbVar7;

  cVar1 = *(char *)((int)param_1 + 8);
  iVar5 = *(int *)param_1;
  if (((cVar1 == '\x02') && (param_3 != 0)) &&
     (iVar3 = iVar5, puVar4 = param_2, *(char *)((int)param_1 + 9) == '\b')) {
    for (; iVar3 != 0; iVar3 = iVar3 + -1) {
      bVar2 = *(byte *)param_2;
      pbVar6 = (byte *)((int)param_2 + 1);
      pbVar7 = (byte *)((int)param_2 + 2);
      param_2 = (void *)((int)param_2 + 3);
      *puVar4 = *(undefined1 *)
                 ((((bVar2 & 0xf8) << 5 | *pbVar6 & 0xf8) << 2 | (int)(uint)*pbVar7 >> 3) + param_3)
      ;
      puVar4 = puVar4 + 1;
    }
  }
  else {
    if (((cVar1 != '\x06') || (param_3 == 0)) ||
       (iVar3 = iVar5, puVar4 = param_2, *(char *)((int)param_1 + 9) != '\b')) {
      if (cVar1 != '\x03') {
        return;
      }
      if (param_4 == 0) {
        return;
      }
      if (*(char *)((int)param_1 + 9) != '\b') {
        return;
      }
      for (; iVar5 != 0; iVar5 = iVar5 + -1) {
        *(byte *)param_2 = *(byte *)((uint)*(byte *)param_2 + param_4);
        param_2 = (void *)((int)param_2 + 1);
      }
      return;
    }
    for (; iVar3 != 0; iVar3 = iVar3 + -1) {
      bVar2 = *(byte *)param_2;
      pbVar6 = (byte *)((int)param_2 + 1);
      pbVar7 = (byte *)((int)param_2 + 2);
      param_2 = (void *)((int)param_2 + 4);
      *puVar4 = *(undefined1 *)
                 ((((bVar2 & 0xf8) << 5 | *pbVar6 & 0xf8) << 2 | (int)(uint)*pbVar7 >> 3) + param_3)
      ;
      puVar4 = puVar4 + 1;
    }
  }
  *(byte *)((int)param_1 + 0xb) = *(byte *)((int)param_1 + 9);
  *(undefined1 *)((int)param_1 + 8) = 3;
  *(undefined1 *)((int)param_1 + 10) = 1;
  *(uint *)((int)param_1 + 4) = (uint)*(byte *)((int)param_1 + 9) * iVar5 + 7 >> 3;
  return;
}
