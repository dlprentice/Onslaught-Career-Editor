/* address: 0x0059ccf3 */
/* name: CDXTexture__MemsetByte */
/* signature: int __stdcall CDXTexture__MemsetByte(int param_1, void * param_2, int param_3, uint param_4) */


int CDXTexture__MemsetByte(int param_1,void *param_2,int param_3,uint param_4)

{
  uint uVar1;
  undefined4 *puVar2;

  puVar2 = param_2;
  for (uVar1 = param_4 >> 2; uVar1 != 0; uVar1 = uVar1 - 1) {
    *puVar2 = CONCAT22(CONCAT11((undefined1)param_3,(undefined1)param_3),
                       CONCAT11((undefined1)param_3,(undefined1)param_3));
    puVar2 = puVar2 + 1;
  }
  for (uVar1 = param_4 & 3; uVar1 != 0; uVar1 = uVar1 - 1) {
    *(undefined1 *)puVar2 = (undefined1)param_3;
    puVar2 = (undefined4 *)((int)puVar2 + 1);
  }
  return (int)param_2;
}
