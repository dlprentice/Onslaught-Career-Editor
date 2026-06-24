/* address: 0x00560f4b */
/* name: CFastVB__Unk_00560f4b */
/* signature: int __cdecl CFastVB__Unk_00560f4b(void * param_1, int param_2, int param_3) */


int __cdecl CFastVB__Unk_00560f4b(void *param_1,int param_2,int param_3)

{
  undefined1 local_2c [24];
  int local_14;
  int local_10;

  CFastVB__Helper_00569b4c
            ((int)*(undefined8 *)param_1,(int)((ulonglong)*(undefined8 *)param_1 >> 0x20),&local_14,
             local_2c);
  CFastVB__Helper_00569ad5
            ((void *)((uint)(local_14 == 0x2d) + param_2),local_10 + param_3,(int)&local_14);
  CFastVB__Unk_00560fa0((void *)param_2,param_3,&local_14,0);
  return param_2;
}
