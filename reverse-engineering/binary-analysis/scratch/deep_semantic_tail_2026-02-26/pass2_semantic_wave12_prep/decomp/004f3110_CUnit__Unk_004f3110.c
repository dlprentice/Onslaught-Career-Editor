/* address: 0x004f3110 */
/* name: CUnit__Unk_004f3110 */
/* signature: int __cdecl CUnit__Unk_004f3110(void * param_1, int param_2, int param_3, void * param_4, int param_5) */


int __cdecl CUnit__Unk_004f3110(void *param_1,int param_2,int param_3,void *param_4,int param_5)

{
  void *file;
  int iVar1;
  int iVar2;
  void *ptr;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_12;
  undefined2 local_c;
  undefined2 local_a;
  undefined2 local_8;
  undefined2 local_6;
  undefined1 local_4;
  undefined1 local_3;

  local_14 = 0;
  local_13 = 0;
  local_12 = 2;
  local_c = 0;
  local_a = 0;
  local_8 = (undefined2)param_3;
  local_6 = SUB42(param_4,0);
  local_4 = 0x18;
  local_3 = 0;
  file = fopen(param_1,&DAT_0063316c);
  if (file != (void *)0x0) {
    fwrite(&local_14,0x12,1,file);
    iVar1 = (int)(param_5 + (param_5 >> 0x1f & 3U)) >> 2;
    if (0 < (int)param_4) {
      param_1 = param_4;
      param_4 = (void *)(((int)param_4 * 4 + -4) * iVar1 + 2 + param_2);
      do {
        iVar2 = param_3;
        ptr = param_4;
        if (0 < param_3) {
          do {
            fwrite((void *)((int)ptr + -2),1,1,file);
            fwrite((void *)((int)ptr + -1),1,1,file);
            fwrite(ptr,1,1,file);
            iVar2 = iVar2 + -1;
            ptr = (void *)((int)ptr + 4);
          } while (iVar2 != 0);
        }
        param_4 = (void *)((int)param_4 + iVar1 * -4);
        param_1 = (void *)((int)param_1 + -1);
      } while (param_1 != (void *)0x0);
    }
    fclose(file);
    return 1;
  }
  return 0;
}
