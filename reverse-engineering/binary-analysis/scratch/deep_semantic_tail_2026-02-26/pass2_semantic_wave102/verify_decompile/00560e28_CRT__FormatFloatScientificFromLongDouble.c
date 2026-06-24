/* address: 0x00560e28 */
/* name: CRT__FormatFloatScientificFromLongDouble */
/* signature: int __cdecl CRT__FormatFloatScientificFromLongDouble(void * param_1, int param_2, int param_3, int param_4) */


int __cdecl
CRT__FormatFloatScientificFromLongDouble(void *param_1,int param_2,int param_3,int param_4)

{
  undefined1 local_2c [24];
  int local_14 [4];

  CFastVB__Helper_00569b4c
            ((int)*(undefined8 *)param_1,(int)((ulonglong)*(undefined8 *)param_1 >> 0x20),local_14,
             local_2c);
  CFastVB__Helper_00569ad5
            ((void *)((uint)(0 < param_3) + param_2 + (uint)(local_14[0] == 0x2d)),param_3 + 1,
             (int)local_14);
  CRT__FormatFloatScientificCore((void *)param_2,param_3,param_4,local_14,0);
  return param_2;
}
