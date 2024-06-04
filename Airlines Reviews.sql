select * from airlines_reviews;

select "Airline Name", count(*) as  "Review Count"
from airlines_reviews
group by "Airline Name"
order by "Review Count" DESC;

select "Airline Name", count(*) as "Positive Recommendations"
from airlines_reviews
where "Recommended" = 'yes'
group by "Airline Name"
order by "Positive Recommendations" desc;

select "Type Of Traveller",
    count(*) as "Review Count",
    avg((("Seat Comfort" + "Cabin Staff Service" + "Food & Beverages" + "Inflight Entertainment" + "Ground Service" + "Value For Money" + "Wifi & Connectivity") / 7)) as "Avg Overall Rating"
from airlines_reviews
where "Type Of Traveller" is not null
group by "Type Of Traveller"
order by "Avg Overall Rating" desc;

select "Customer Name", "Post Date", "Country", "Type Of Traveller", "Title", "Airline Name", "Recommended"
from airlines_reviews
WHERE EXTRACT(YEAR FROM TO_DATE("Post Date", 'YYYY-MM-DD')) = 2023;