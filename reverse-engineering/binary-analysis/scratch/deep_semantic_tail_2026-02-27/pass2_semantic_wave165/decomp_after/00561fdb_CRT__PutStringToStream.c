/* address: 0x00561fdb */
/* name: CRT__PutStringToStream */
/* signature: void __cdecl CRT__PutStringToStream(void * param_1, int param_2, void * param_3, void * param_4) */


void __cdecl CRT__PutStringToStream(void *param_1,int param_2,void *param_3,void *param_4)

{
  char cVar1;

  do {
    if (param_2 < 1) {
      return;
    }
    param_2 = param_2 + -1;
    cVar1 = *(char *)param_1;
    param_1 = (void *)((int)param_1 + 1);
    CRT__PutCharToStreamAndCount((int)cVar1,param_3,param_4);
  } while (*(int *)param_4 != -1);
  return;
}
