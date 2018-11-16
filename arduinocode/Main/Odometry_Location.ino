
extern volatile long right_count;
extern volatile long left_count;

void printstuff()
{
  Serial.println("hello");
  Serial.println(right_count);
}
